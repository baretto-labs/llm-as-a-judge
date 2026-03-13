package fr.baretto.benchmarks;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import fr.baretto.benchmarks.strategy.model.VariableScope;
import fr.baretto.benchmarks.strategy.model.ParsedLocalVariable;

/**
 * Tests unitaires pour le tracking des variables locales et la résolution CALLS améliorée.
 *
 * Ces tests valident :
 * 1. Le fonctionnement de VariableScope
 * 2. Le modèle ParsedLocalVariable
 * 3. La résolution des appels de méthodes avec variables locales
 */
public class TestVariableScopeResolution {

    private VariableScope scope;

    @BeforeEach
    public void setUp() {
        scope = new VariableScope();
    }

    // ==================== Tests VariableScope ====================

    @Test
    public void testVariableScopeAddAndGet() {
        // Ajouter des variables au scope
        scope.addVariable("user", "com.example.User");
        scope.addVariable("count", "java.lang.Integer");
        scope.addVariable("name", "java.lang.String");

        // Vérifier que les variables sont présentes
        assertTrue(scope.hasVariable("user"));
        assertTrue(scope.hasVariable("count"));
        assertTrue(scope.hasVariable("name"));
        assertFalse(scope.hasVariable("unknown"));

        // Vérifier les types résolus
        assertEquals("com.example.User", scope.getVariableType("user"));
        assertEquals("java.lang.Integer", scope.getVariableType("count"));
        assertEquals("java.lang.String", scope.getVariableType("name"));
        assertNull(scope.getVariableType("unknown"));
    }

    @Test
    public void testVariableScopeEmpty() {
        // Scope vide
        assertFalse(scope.hasVariable("anything"));
        assertNull(scope.getVariableType("anything"));
    }

    @Test
    public void testVariableScopeOverwrite() {
        // Ajouter une variable
        scope.addVariable("value", "java.lang.Integer");
        assertEquals("java.lang.Integer", scope.getVariableType("value"));

        // Écraser avec un autre type (simule shadowing)
        scope.addVariable("value", "java.lang.String");
        assertEquals("java.lang.String", scope.getVariableType("value"));
    }

    @Test
    public void testVariableScopeWithParameters() {
        // Simuler un scope avec paramètres de méthode
        scope.addVariable("request", "javax.servlet.http.HttpServletRequest");
        scope.addVariable("response", "javax.servlet.http.HttpServletResponse");
        scope.addVariable("id", "java.lang.Long");

        // Ajouter des variables locales
        scope.addVariable("user", "com.example.User");
        scope.addVariable("result", "java.lang.String");

        // Vérifier que tout est accessible
        assertEquals("javax.servlet.http.HttpServletRequest", scope.getVariableType("request"));
        assertEquals("com.example.User", scope.getVariableType("user"));
        assertTrue(scope.hasVariable("response"));
        assertTrue(scope.hasVariable("id"));
        assertTrue(scope.hasVariable("result"));
    }

    // ==================== Tests ParsedLocalVariable ====================

    @Test
    public void testParsedLocalVariableCreation() {
        ParsedLocalVariable var = new ParsedLocalVariable("count", "int");

        assertEquals("count", var.name);
        assertEquals("int", var.type);
        assertNull(var.resolvedType); // Pas encore résolu
        assertEquals(0, var.declarationLine); // Valeur par défaut
    }

    @Test
    public void testParsedLocalVariableWithResolvedType() {
        ParsedLocalVariable var = new ParsedLocalVariable("user", "User");
        var.resolvedType = "com.example.model.User";
        var.declarationLine = 42;

        assertEquals("user", var.name);
        assertEquals("User", var.type);
        assertEquals("com.example.model.User", var.resolvedType);
        assertEquals(42, var.declarationLine);
    }

    // ==================== Tests de scénarios réels ====================

    @Test
    public void testScenarioSimpleMethodWithLocalVariable() {
        // Simule: void processUser() {
        //   User user = repository.findById(1);
        //   user.save();
        // }

        VariableScope methodScope = new VariableScope();

        // Variable locale déclarée
        methodScope.addVariable("user", "com.example.model.User");

        // Lors de la résolution de "user.save()"
        assertTrue(methodScope.hasVariable("user"));
        String userType = methodScope.getVariableType("user");
        assertEquals("com.example.model.User", userType);

        // On peut maintenant chercher la méthode "save" dans la classe User
        assertNotNull(userType);
    }

    @Test
    public void testScenarioMethodWithParametersAndLocalVariables() {
        // Simule: void updateUser(Long id, String newName) {
        //   User user = userRepository.findById(id);
        //   String oldName = user.getName();
        //   user.setName(newName);
        //   userRepository.save(user);
        // }

        VariableScope methodScope = new VariableScope();

        // Paramètres de méthode
        methodScope.addVariable("id", "java.lang.Long");
        methodScope.addVariable("newName", "java.lang.String");

        // Variables locales
        methodScope.addVariable("user", "com.example.model.User");
        methodScope.addVariable("oldName", "java.lang.String");

        // Vérifications
        assertTrue(methodScope.hasVariable("id"));
        assertTrue(methodScope.hasVariable("newName"));
        assertTrue(methodScope.hasVariable("user"));
        assertTrue(methodScope.hasVariable("oldName"));

        // Vérifier les types pour résolution CALLS
        assertEquals("java.lang.Long", methodScope.getVariableType("id"));
        assertEquals("com.example.model.User", methodScope.getVariableType("user"));
        assertEquals("java.lang.String", methodScope.getVariableType("oldName"));
    }

    @Test
    public void testScenarioComplexMethodWithMultipleVariables() {
        // Simule une méthode avec plusieurs variables locales de types différents
        VariableScope methodScope = new VariableScope();

        // Variables locales
        methodScope.addVariable("list", "java.util.List");
        methodScope.addVariable("map", "java.util.HashMap");
        methodScope.addVariable("builder", "java.lang.StringBuilder");
        methodScope.addVariable("count", "java.lang.Integer");
        methodScope.addVariable("result", "java.lang.String");

        // Pour chaque appel de méthode, on peut résoudre le receiver
        // list.add(...) → type = java.util.List
        assertEquals("java.util.List", methodScope.getVariableType("list"));

        // map.put(...) → type = java.util.HashMap
        assertEquals("java.util.HashMap", methodScope.getVariableType("map"));

        // builder.append(...) → type = java.lang.StringBuilder
        assertEquals("java.lang.StringBuilder", methodScope.getVariableType("builder"));

        // count.intValue() → type = java.lang.Integer
        assertEquals("java.lang.Integer", methodScope.getVariableType("count"));
    }

    @Test
    public void testScenarioFieldVsLocalVariable() {
        // Simule: class Service {
        //   private UserRepository repository; // field
        //
        //   void method() {
        //     User user = repository.findById(1); // local
        //     repository.save(user); // appel sur field
        //     user.getName(); // appel sur local
        //   }
        // }

        VariableScope methodScope = new VariableScope();

        // Variable locale (pas le field "repository")
        methodScope.addVariable("user", "com.example.model.User");

        // "repository" n'est PAS dans le scope (c'est un field)
        assertFalse(methodScope.hasVariable("repository"));

        // "user" est dans le scope (variable locale)
        assertTrue(methodScope.hasVariable("user"));
        assertEquals("com.example.model.User", methodScope.getVariableType("user"));
    }

    @Test
    public void testScenarioChainedMethodCalls() {
        // Simule: String result = user.getName().toLowerCase().trim();
        // Seul "user" est une variable locale, le reste sont des appels chaînés

        VariableScope methodScope = new VariableScope();
        methodScope.addVariable("user", "com.example.model.User");
        methodScope.addVariable("result", "java.lang.String");

        // Premier appel: user.getName() → receiver = "user"
        assertTrue(methodScope.hasVariable("user"));
        assertEquals("com.example.model.User", methodScope.getVariableType("user"));

        // Les appels suivants (.toLowerCase(), .trim()) ne sont pas des variables
        assertFalse(methodScope.hasVariable("getName"));
        assertFalse(methodScope.hasVariable("toLowerCase"));
        assertFalse(methodScope.hasVariable("trim"));
    }
}
