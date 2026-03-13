package fr.baretto.benchmarks;

import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import org.junit.jupiter.api.*;
import org.neo4j.dbms.api.DatabaseManagementService;
import org.neo4j.dbms.api.DatabaseManagementServiceBuilder;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Result;
import org.neo4j.graphdb.Transaction;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Comparator;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Test JUnit avec des exemples complets de requêtes Cypher pour interroger le graphe de code.
 * Ce test sert de documentation vivante montrant comment utiliser le graphe Neo4j.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class TestCypherExamples {

    private static final String DB_PATH = "./neo4j-db";
    private Path testDir;
    private DatabaseManagementService managementService;
    private GraphDatabaseService graphDb;

    @BeforeAll
    void setup() throws Exception {
        System.out.println("\n╔═══════════════════════════════════════════════════════════╗");
        System.out.println("║  TEST CYPHER - Exemples de Requêtes Complètes            ║");
        System.out.println("╚═══════════════════════════════════════════════════════════╝\n");

        // Nettoyer et créer un projet de test complet
        cleanAll();

        testDir = Paths.get("test-cypher-examples");
        Files.createDirectories(testDir);

        // Créer un mini-projet Java réaliste avec plusieurs fichiers
        createTestProject();

        // Indexer
        System.out.println("📂 Indexation du projet de test...");
        Neo4jGraphRagStrategy strategy = new Neo4jGraphRagStrategy(DB_PATH);
        strategy.indexDirectory(testDir);
        strategy.shutdown();
        System.out.println("✅ Indexation terminée\n");

        // Se connecter à Neo4j
        Path dbPath = Paths.get(DB_PATH).toAbsolutePath().normalize();
        managementService = new DatabaseManagementServiceBuilder(dbPath).build();
        graphDb = managementService.database("neo4j");
    }

    @AfterAll
    void tearDown() throws IOException {
        if (managementService != null) {
            managementService.shutdown();
        }
        cleanTestFiles();
    }

    /**
     * Crée un mini-projet Java avec plusieurs classes pour tester les requêtes Cypher.
     */
    private void createTestProject() throws IOException {
        // Package models
        Path modelsDir = testDir.resolve("models");
        Files.createDirectories(modelsDir);

        // Classe User avec attributs et méthodes
        String userCode = """
            package com.example.models;

            public class User {
                private String name;
                private String email;
                private int age;

                public User(String name, String email) {
                    this.name = name;
                    this.email = email;
                    this.age = 0;
                }

                public String getName() {
                    return name;
                }

                public void setName(String name) {
                    this.name = name;
                }

                public String getEmail() {
                    return email;
                }

                public void setEmail(String email) {
                    this.email = email;
                }

                public int getAge() {
                    return age;
                }

                public void setAge(int age) {
                    this.age = age;
                }

                public boolean isAdult() {
                    return age >= 18;
                }

                public String toString() {
                    return name + " <" + email + ">";
                }
            }
            """;
        Files.writeString(modelsDir.resolve("User.java"), userCode);

        // Classe Product
        String productCode = """
            package com.example.models;

            public class Product {
                private String id;
                private String name;
                private double price;

                public Product(String id, String name, double price) {
                    this.id = id;
                    this.name = name;
                    this.price = price;
                }

                public String getId() {
                    return id;
                }

                public String getName() {
                    return name;
                }

                public double getPrice() {
                    return price;
                }

                public void setPrice(double price) {
                    this.price = price;
                }

                public double calculateDiscount(double percentage) {
                    return price * (percentage / 100.0);
                }
            }
            """;
        Files.writeString(modelsDir.resolve("Product.java"), productCode);

        // Package services
        Path servicesDir = testDir.resolve("services");
        Files.createDirectories(servicesDir);

        // Classe UserService avec dépendances
        String userServiceCode = """
            package com.example.services;

            import com.example.models.User;

            public class UserService {
                private UserRepository repository;

                public UserService(UserRepository repository) {
                    this.repository = repository;
                }

                public User createUser(String name, String email) {
                    User user = new User(name, email);
                    repository.save(user);
                    return user;
                }

                public User findByEmail(String email) {
                    return repository.findByEmail(email);
                }

                public void updateUser(User user, String newName) {
                    user.setName(newName);
                    repository.update(user);
                }

                public boolean validateAge(User user) {
                    return user.isAdult();
                }
            }
            """;
        Files.writeString(servicesDir.resolve("UserService.java"), userServiceCode);

        // Interface UserRepository
        String repositoryCode = """
            package com.example.services;

            import com.example.models.User;

            public interface UserRepository {
                void save(User user);
                void update(User user);
                User findByEmail(String email);
                void delete(User user);
            }
            """;
        Files.writeString(servicesDir.resolve("UserRepository.java"), repositoryCode);

        System.out.println("✅ Projet de test créé:");
        System.out.println("   - 2 classes dans models (User, Product)");
        System.out.println("   - 1 classe + 1 interface dans services");
        System.out.println("   - ~20 méthodes au total\n");
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // EXEMPLES DE REQUÊTES CYPHER COMPLÈTES
    // ═══════════════════════════════════════════════════════════════════════════

    @Test
    @Order(1)
    @DisplayName("Exemple 1: Trouver toutes les classes et leurs attributs")
    void exemple1_ClassesEtAttributs() {
        System.out.println("\n📋 EXEMPLE 1: Trouver toutes les classes et leurs attributs");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (c:Class)-[:DECLARES]->(p:Property)
            RETURN c.name as classe,
                   collect(p.name) as attributs,
                   count(p) as nbAttributs
            ORDER BY nbAttributs DESC
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                System.out.println(String.format("  • %s: %s (%d attributs)",
                    row.get("classe"),
                    row.get("attributs"),
                    row.get("nbAttributs")));
            }

            // Assertions : on doit avoir au moins 2 classes avec des attributs
            assertTrue(count >= 2, "Il devrait y avoir au moins 2 classes avec des attributs");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(2)
    @DisplayName("Exemple 2: Trouver toutes les méthodes d'une classe spécifique")
    void exemple2_MethodesDuneClasse() {
        System.out.println("\n📋 EXEMPLE 2: Trouver toutes les méthodes de la classe User");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (c:Class {name: 'User'})-[:DECLARES]->(m)
            WHERE m:Function OR m:Constructor
            OPTIONAL MATCH (m)-[:RETURNS]->(returnType)
            OPTIONAL MATCH (m)-[:HAS_PARAMETER]->(param:Parameter)
            RETURN m.name as methode,
                   labels(m)[0] as type,
                   returnType.name as typeRetour,
                   collect(param.name) as parametres,
                   m.signature as signature
            ORDER BY methode
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int count = 0;
            boolean hasGetName = false;
            boolean hasSetName = false;
            boolean hasConstructor = false;

            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                String methodName = (String) row.get("methode");

                System.out.println(String.format("  %d. %s (%s)",
                    count,
                    methodName,
                    row.get("type")));
                System.out.println(String.format("     Retourne: %s", row.get("typeRetour")));
                System.out.println(String.format("     Paramètres: %s", row.get("parametres")));

                if ("getName".equals(methodName)) hasGetName = true;
                if ("setName".equals(methodName)) hasSetName = true;
                if ("User".equals(methodName)) hasConstructor = true;
            }

            // Assertions : User devrait avoir au moins ces méthodes de base
            assertTrue(count >= 8, "User devrait avoir au moins 8 méthodes (getters, setters, constructeur, etc.)");
            assertTrue(hasGetName, "User devrait avoir la méthode getName()");
            assertTrue(hasSetName, "User devrait avoir la méthode setName()");
            assertTrue(hasConstructor, "User devrait avoir un constructeur");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(3)
    @DisplayName("Exemple 3: Rechercher des méthodes par nom (getters)")
    void exemple3_RechercheParNom() {
        System.out.println("\n📋 EXEMPLE 3: Rechercher tous les getters (getName, getEmail, etc.)");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (c:Class)-[:DECLARES]->(f:Function)
            WHERE f.name STARTS WITH 'get'
            OPTIONAL MATCH (f)-[:RETURNS]->(returnType)
            RETURN c.name as classe,
                   f.name as getter,
                   returnType.name as typeRetour,
                   f.fqn as fqn
            ORDER BY classe, getter
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                System.out.println(String.format("  • %s.%s() → %s",
                    row.get("classe"),
                    row.get("getter"),
                    row.get("typeRetour")));
            }

            // Assertions : on devrait avoir au moins 6 getters (User: getName, getEmail, getAge; Product: getId, getName, getPrice)
            assertTrue(count >= 6, "Il devrait y avoir au moins 6 getters dans le projet");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(4)
    @DisplayName("Exemple 4: Trouver les dépendances entre classes (CALLS)")
    void exemple4_DependancesEntreClasses() {
        System.out.println("\n📋 EXEMPLE 4: Trouver quelles classes utilisent la classe User");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (caller:Function)-[:CALLS]->(callee:Function)
            WHERE callee.fqn STARTS WITH 'com.example.models.User.'
            MATCH (callerClass:Class)-[:DECLARES]->(caller)
            MATCH (calleeClass:Class)-[:DECLARES]->(callee)
            RETURN DISTINCT callerClass.name as classeAppelante,
                   calleeClass.name as classeAppelee,
                   count(*) as nbAppels
            ORDER BY nbAppels DESC
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                System.out.println(String.format("  • %s → %s (%d appels)",
                    row.get("classeAppelante"),
                    row.get("classeAppelee"),
                    row.get("nbAppels")));
            }

            // Note: Cette requête peut retourner 0 si les CALLS ne sont pas résolus
            // On ne fait pas d'assertion stricte ici
            System.out.println("   (Résultats: " + count + " dépendances trouvées)");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(5)
    @DisplayName("Exemple 5: Analyser les méthodes par nombre de paramètres")
    void exemple5_MethodesParNbParametres() {
        System.out.println("\n📋 EXEMPLE 5: Lister les méthodes avec 2+ paramètres");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (c:Class)-[:DECLARES]->(f:Function)
            OPTIONAL MATCH (f)-[:HAS_PARAMETER]->(p:Parameter)
            WITH c, f, count(p) as nbParams
            WHERE nbParams >= 2
            RETURN c.name as classe,
                   f.name as methode,
                   nbParams as nbParametres,
                   f.fqn as fqn
            ORDER BY nbParams DESC, classe, methode
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                System.out.println(String.format("  • %s.%s() avec %d paramètres",
                    row.get("classe"),
                    row.get("methode"),
                    row.get("nbParametres")));
            }

            // Assertions : on devrait avoir au moins 2 méthodes avec 2+ paramètres
            assertTrue(count >= 2, "Il devrait y avoir au moins 2 méthodes avec 2+ paramètres");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(6)
    @DisplayName("Exemple 6: Trouver les classes dans un package")
    void exemple6_ClassesDansPackage() {
        System.out.println("\n📋 EXEMPLE 6: Lister toutes les classes du package models");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (pkg:Package)-[:CONTAINS]->(c:Class)
            WHERE pkg.name = 'com.example.models'
            OPTIONAL MATCH (c)-[:DECLARES]->(m)
            WHERE m:Function OR m:Constructor
            RETURN c.name as classe,
                   c.fqn as fqn,
                   count(DISTINCT m) as nbMethodes,
                   labels(c) as labels
            ORDER BY classe
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int count = 0;
            boolean hasUser = false;
            boolean hasProduct = false;

            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                String className = (String) row.get("classe");

                System.out.println(String.format("  • %s (%d méthodes)",
                    className,
                    row.get("nbMethodes")));
                System.out.println(String.format("    FQN: %s", row.get("fqn")));

                if ("User".equals(className)) hasUser = true;
                if ("Product".equals(className)) hasProduct = true;
            }

            // Assertions : le package models devrait contenir User et Product
            assertTrue(count >= 2, "Le package models devrait contenir au moins 2 classes");
            assertTrue(hasUser, "Le package models devrait contenir la classe User");
            assertTrue(hasProduct, "Le package models devrait contenir la classe Product");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(7)
    @DisplayName("Exemple 7: Trouver les interfaces et leurs implémentations")
    void exemple7_InterfacesEtImplementations() {
        System.out.println("\n📋 EXEMPLE 7: Trouver les interfaces et qui les implémente");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (iface:Interface)
            OPTIONAL MATCH (impl:Class)-[:IMPLEMENTS]->(iface)
            OPTIONAL MATCH (iface)-[:DECLARES]->(m:Function)
            RETURN iface.name as interface,
                   iface.fqn as fqn,
                   collect(DISTINCT impl.name) as implementations,
                   collect(DISTINCT m.name) as methodes
            ORDER BY interface
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int count = 0;
            boolean hasUserRepository = false;

            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                String interfaceName = (String) row.get("interface");

                System.out.println(String.format("  Interface: %s", interfaceName));
                System.out.println(String.format("    Méthodes: %s", row.get("methodes")));
                System.out.println(String.format("    Implémentée par: %s", row.get("implementations")));

                if ("UserRepository".equals(interfaceName)) hasUserRepository = true;
            }

            // Assertions : on devrait avoir au moins UserRepository
            assertTrue(count >= 1, "Il devrait y avoir au moins 1 interface");
            assertTrue(hasUserRepository, "L'interface UserRepository devrait exister");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(8)
    @DisplayName("Exemple 8: Analyser la complexité des méthodes (appels sortants)")
    void exemple8_ComplexiteMethodes() {
        System.out.println("\n📋 EXEMPLE 8: Méthodes triées par nombre d'appels sortants");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (c:Class)-[:DECLARES]->(f:Function)
            OPTIONAL MATCH (f)-[:CALLS]->(called)
            WITH c, f, count(called) as nbAppels
            WHERE nbAppels > 0
            RETURN c.name as classe,
                   f.name as methode,
                   nbAppels as nbAppelsSortants,
                   f.fqn as fqn
            ORDER BY nbAppels DESC, classe, methode
            LIMIT 10
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats (Top 10):");
            int rank = 1;
            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                System.out.println(String.format("  %d. %s.%s() - %d appels",
                    rank++,
                    row.get("classe"),
                    row.get("methode"),
                    row.get("nbAppelsSortants")));
            }

            // Note: Si les CALLS ne sont pas résolus, ce test retournera 0
            // On affiche juste le résultat sans assertion stricte
            System.out.println("   (Méthodes avec appels sortants: " + count + ")");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(9)
    @DisplayName("Exemple 9: Trouver les méthodes les plus appelées")
    void exemple9_MethodesLesPlusAppelees() {
        System.out.println("\n📋 EXEMPLE 9: Top méthodes les plus appelées dans le projet");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (caller:Function)-[:CALLS]->(f:Function)
            MATCH (c:Class)-[:DECLARES]->(f)
            WITH c, f, count(caller) as nbAppelsEntrants
            RETURN c.name as classe,
                   f.name as methode,
                   nbAppelsEntrants as popularite,
                   f.fqn as fqn
            ORDER BY popularite DESC
            LIMIT 10
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int rank = 1;
            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                System.out.println(String.format("  %d. %s.%s() - appelée %d fois",
                    rank++,
                    row.get("classe"),
                    row.get("methode"),
                    row.get("popularite")));
            }

            // Note: Si les CALLS ne sont pas résolus, ce test retournera 0
            System.out.println("   (Méthodes appelées: " + count + ")");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(10)
    @DisplayName("Exemple 10: Navigation complète - Package → Class → Method → Calls")
    void exemple10_NavigationComplete() {
        System.out.println("\n📋 EXEMPLE 10: Navigation complète dans le graphe");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH path = (pkg:Package)-[:CONTAINS]->(c:Class)-[:DECLARES]->(f:Function)-[:CALLS]->(called:Function)
            WHERE pkg.name STARTS WITH 'com.example.services'
            MATCH (calledClass:Class)-[:DECLARES]->(called)
            RETURN pkg.name as package,
                   c.name as classe,
                   f.name as methode,
                   called.name as appellee,
                   calledClass.name as classeAppelee
            LIMIT 5
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats (chemins complets):");
            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                System.out.println(String.format("  📦 %s", row.get("package")));
                System.out.println(String.format("    └─ 📂 %s", row.get("classe")));
                System.out.println(String.format("       └─ ⚙️  %s()", row.get("methode")));
                System.out.println(String.format("          └─ 🔗 appelle %s.%s()",
                    row.get("classeAppelee"),
                    row.get("appellee")));
            }

            // Note: Si les CALLS ne sont pas résolus, ce test retournera 0
            System.out.println("   (Chemins trouvés: " + count + ")");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(11)
    @DisplayName("Exemple 11: Trouver des patterns spécifiques (méthodes boolean)")
    void exemple11_PatternsSpecifiques() {
        System.out.println("\n📋 EXEMPLE 11: Trouver toutes les méthodes qui retournent boolean");
        System.out.println("─────────────────────────────────────────────────────────────");

        String cypher = """
            MATCH (c:Class)-[:DECLARES]->(f:Function)-[:RETURNS]->(t)
            WHERE t.name = 'boolean'
            OPTIONAL MATCH (f)-[:HAS_PARAMETER]->(p:Parameter)
            RETURN c.name as classe,
                   f.name as methode,
                   collect(p.name) as parametres,
                   f.fqn as fqn
            ORDER BY classe, methode
            """;

        System.out.println("Requête Cypher:");
        System.out.println(cypher);

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(cypher);

            System.out.println("\nRésultats:");
            int count = 0;
            boolean hasIsAdult = false;
            boolean hasValidateAge = false;

            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                count++;
                String methodName = (String) row.get("methode");

                System.out.println(String.format("  • %s.%s(%s) → boolean",
                    row.get("classe"),
                    methodName,
                    row.get("parametres")));

                if ("isAdult".equals(methodName)) hasIsAdult = true;
                if ("validateAge".equals(methodName)) hasValidateAge = true;
            }

            // Assertions : on devrait avoir au moins 2 méthodes boolean
            assertTrue(count >= 2, "Il devrait y avoir au moins 2 méthodes qui retournent boolean");
            assertTrue(hasIsAdult, "La méthode isAdult() devrait exister");
            assertTrue(hasValidateAge, "La méthode validateAge() devrait exister");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(12)
    @DisplayName("Exemple 12: Statistiques globales du projet")
    void exemple12_StatistiquesGlobales() {
        System.out.println("\n📋 EXEMPLE 12: Statistiques complètes du projet");
        System.out.println("─────────────────────────────────────────────────────────────");

        try (Transaction tx = graphDb.beginTx()) {
            // Statistique 1: Nombre de classes
            Result r1 = tx.execute("MATCH (c:Class) RETURN count(c) as nb");
            long nbClasses = r1.hasNext() ? (Long) r1.next().get("nb") : 0;

            // Statistique 2: Nombre de méthodes
            Result r2 = tx.execute("MATCH (f:Function) RETURN count(f) as nb");
            long nbMethodes = r2.hasNext() ? (Long) r2.next().get("nb") : 0;

            // Statistique 3: Nombre d'attributs
            Result r3 = tx.execute("MATCH (p:Property) RETURN count(p) as nb");
            long nbAttributs = r3.hasNext() ? (Long) r3.next().get("nb") : 0;

            // Statistique 4: Nombre d'interfaces
            Result r4 = tx.execute("MATCH (i:Interface) RETURN count(i) as nb");
            long nbInterfaces = r4.hasNext() ? (Long) r4.next().get("nb") : 0;

            // Statistique 5: Nombre de relations CALLS
            Result r5 = tx.execute("MATCH ()-[c:CALLS]->() RETURN count(c) as nb");
            long nbCalls = r5.hasNext() ? (Long) r5.next().get("nb") : 0;

            // Statistique 6: Nombre de packages
            Result r6 = tx.execute("MATCH (pkg:Package) RETURN count(pkg) as nb");
            long nbPackages = r6.hasNext() ? (Long) r6.next().get("nb") : 0;

            System.out.println("\nStatistiques:");
            System.out.println(String.format("  📦 Packages:    %d", nbPackages));
            System.out.println(String.format("  📂 Classes:     %d", nbClasses));
            System.out.println(String.format("  🔌 Interfaces:  %d", nbInterfaces));
            System.out.println(String.format("  ⚙️  Méthodes:    %d", nbMethodes));
            System.out.println(String.format("  📊 Attributs:   %d", nbAttributs));
            System.out.println(String.format("  🔗 Appels:      %d", nbCalls));

            // Assertions : vérifier que le graphe contient les éléments de base
            assertTrue(nbPackages >= 2, "Il devrait y avoir au moins 2 packages (models, services)");
            assertTrue(nbClasses >= 3, "Il devrait y avoir au moins 3 classes (User, Product, UserService)");
            assertTrue(nbInterfaces >= 1, "Il devrait y avoir au moins 1 interface (UserRepository)");
            assertTrue(nbMethodes >= 15, "Il devrait y avoir au moins 15 méthodes dans le projet");
            assertTrue(nbAttributs >= 7, "Il devrait y avoir au moins 7 attributs (User: 3, Product: 3, UserService: 1)");
            // Note: nbCalls peut être 0 si les CALLS ne sont pas résolus

            tx.commit();
        }
        System.out.println();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // MÉTHODES UTILITAIRES
    // ═══════════════════════════════════════════════════════════════════════════

    private void cleanAll() {
        cleanDatabase();
        cleanTestFiles();
    }

    private void cleanDatabase() {
        try {
            Path dbPath = Paths.get(DB_PATH).toAbsolutePath().normalize();
            if (Files.exists(dbPath)) {
                Files.walk(dbPath)
                    .sorted(Comparator.reverseOrder())
                    .forEach(path -> {
                        try {
                            Files.delete(path);
                        } catch (IOException e) {
                            // Ignore
                        }
                    });
            }
        } catch (IOException e) {
            System.err.println("Erreur nettoyage base: " + e.getMessage());
        }
    }

    private void cleanTestFiles() {
        try {
            Path testPath = Paths.get("test-cypher-examples");
            if (Files.exists(testPath)) {
                Files.walk(testPath)
                    .sorted(Comparator.reverseOrder())
                    .forEach(path -> {
                        try {
                            Files.delete(path);
                        } catch (IOException e) {
                            // Ignore
                        }
                    });
            }
        } catch (IOException e) {
            System.err.println("Erreur nettoyage fichiers: " + e.getMessage());
        }
    }
}
