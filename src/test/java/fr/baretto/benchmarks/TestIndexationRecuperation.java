package fr.baretto.benchmarks;

import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import org.junit.jupiter.api.*;
import org.neo4j.dbms.api.DatabaseManagementService;
import org.neo4j.dbms.api.DatabaseManagementServiceBuilder;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Node;
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
 * Test unitaire simple d'indexation et récupération de données.
 * Point de départ pour le debug du graphe Neo4j.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class TestIndexationRecuperation {

    // Utiliser le même chemin que Neo4jGraphRagStrategy
    private static final String DB_PATH = "./neo4j-db";
    private Path testDir;
    private DatabaseManagementService managementService;
    private GraphDatabaseService graphDb;

    @BeforeAll
    void setup() {
        System.out.println("\n=== DÉBUT DU TEST D'INDEXATION ===\n");
    }

    @Test
    @Order(1)
    @DisplayName("Étape 1: Créer le fichier de test")
    void etape1_CreerFichier() throws IOException {
        System.out.println("ÉTAPE 1: Création du fichier Java de test");

        // Nettoyer la base Neo4j et les fichiers de test
        cleanDatabase();
        cleanTestFiles();

        // Créer le répertoire de test
        testDir = Paths.get("test-indexation-simple");
        Files.createDirectories(testDir);

        // Créer un fichier Java ultra-simple
        String javaCode = """
            package com.example;

            public class Calculator {
                private int value;

                public Calculator() {
                    this.value = 0;
                }

                public int add(int a, int b) {
                    return a + b;
                }

                public int getValue() {
                    return value;
                }

                public void setValue(int value) {
                    this.value = value;
                }
            }
            """;

        Path javaFile = testDir.resolve("Calculator.java");
        Files.writeString(javaFile, javaCode);

        assertTrue(Files.exists(javaFile), "Le fichier Java devrait être créé");
        System.out.println("✅ Fichier créé: " + javaFile);
        System.out.println("   - Package: com.example");
        System.out.println("   - Classe: Calculator");
        System.out.println("   - 1 field: value");
        System.out.println("   - 1 constructeur");
        System.out.println("   - 3 méthodes: add, getValue, setValue\n");
    }

    @Test
    @Order(2)
    @DisplayName("Étape 2: Indexer avec Neo4jGraphRagStrategy")
    void etape2_Indexer() throws Exception {
        System.out.println("ÉTAPE 2: Indexation avec Neo4jGraphRagStrategy");

        Neo4jGraphRagStrategy strategy = new Neo4jGraphRagStrategy(DB_PATH);

        System.out.println("Lancement de l'indexation...");
        long startTime = System.currentTimeMillis();

        strategy.indexDirectory(testDir);

        long duration = System.currentTimeMillis() - startTime;
        System.out.println("✅ Indexation terminée en " + duration + "ms");

        // Fermer la connexion Neo4j pour libérer le lock
        System.out.println("Fermeture de la connexion Neo4j...");
        strategy.shutdown();
        System.out.println("✅ Connexion fermée\n");
    }

    @Test
    @Order(3)
    @DisplayName("Étape 3: Ouvrir la connexion Neo4j")
    void etape3_OuvrirConnexion() {
        System.out.println("ÉTAPE 3: Connexion à Neo4j");

        Path dbPath = Paths.get(DB_PATH).toAbsolutePath().normalize();
        managementService = new DatabaseManagementServiceBuilder(dbPath).build();
        graphDb = managementService.database("neo4j");

        assertNotNull(graphDb, "La connexion Neo4j devrait être établie");
        System.out.println("✅ Connexion établie\n");
    }

    @Test
    @Order(4)
    @DisplayName("Étape 4: Vérifier les nœuds de base")
    void etape4_VerifierNoeuds() {
        System.out.println("ÉTAPE 4: Vérification des nœuds créés");

        try (Transaction tx = graphDb.beginTx()) {
            // Compter tous les nœuds
            Result allNodes = tx.execute("MATCH (n) RETURN count(n) as total");
            long totalNodes = allNodes.hasNext() ? (Long) allNodes.next().get("total") : 0;
            System.out.println("Total de nœuds: " + totalNodes);

            // Compter par label
            Result labelCounts = tx.execute(
                "MATCH (n) " +
                "UNWIND labels(n) as label " +
                "RETURN label, count(*) as count " +
                "ORDER BY count DESC"
            );

            System.out.println("\nNœuds par label:");
            while (labelCounts.hasNext()) {
                Map<String, Object> row = labelCounts.next();
                System.out.println("  " + row.get("label") + ": " + row.get("count"));
            }

            // Vérifications spécifiques
            Result classResult = tx.execute("MATCH (c:Class {name: 'Calculator'}) RETURN count(c) as count");
            long classCount = classResult.hasNext() ? (Long) classResult.next().get("count") : 0;

            Result functionResult = tx.execute(
                "MATCH (f:Function) WHERE f.fqn STARTS WITH 'com.example.Calculator.' RETURN count(f) as count"
            );
            long functionCount = functionResult.hasNext() ? (Long) functionResult.next().get("count") : 0;

            Result propertyResult = tx.execute("MATCH (p:Property {name: 'value'}) RETURN count(p) as count");
            long propertyCount = propertyResult.hasNext() ? (Long) propertyResult.next().get("count") : 0;

            System.out.println("\n✅ Vérifications:");
            System.out.println("  Classe 'Calculator': " + classCount + " (attendu: 1)");
            System.out.println("  Fonctions: " + functionCount + " (attendu: 3)");
            System.out.println("  Property 'value': " + propertyCount + " (attendu: 1)");

            assertTrue(totalNodes > 0, "Il devrait y avoir des nœuds dans la base");
            assertEquals(1, classCount, "Il devrait y avoir 1 classe Calculator");
            assertTrue(functionCount >= 3, "Il devrait y avoir au moins 3 fonctions");
            assertEquals(1, propertyCount, "Il devrait y avoir 1 property 'value'");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(5)
    @DisplayName("Étape 5: Vérifier les relations DECLARES")
    void etape5_VerifierDeclares() {
        System.out.println("ÉTAPE 5: Vérification des relations DECLARES");

        try (Transaction tx = graphDb.beginTx()) {
            // Compter toutes les relations
            Result allRels = tx.execute("MATCH ()-[r]->() RETURN count(r) as total");
            long totalRels = allRels.hasNext() ? (Long) allRels.next().get("total") : 0;
            System.out.println("Total de relations: " + totalRels);

            // Compter par type
            Result relTypes = tx.execute(
                "MATCH ()-[r]->() " +
                "RETURN type(r) as relType, count(r) as count " +
                "ORDER BY count DESC"
            );

            System.out.println("\nRelations par type:");
            while (relTypes.hasNext()) {
                Map<String, Object> row = relTypes.next();
                System.out.println("  " + row.get("relType") + ": " + row.get("count"));
            }

            // Vérifier DECLARES spécifiquement
            Result declaresResult = tx.execute(
                "MATCH (c:Class {name: 'Calculator'})-[:DECLARES]->(target) " +
                "RETURN count(target) as count"
            );
            long declaresCount = declaresResult.hasNext() ? (Long) declaresResult.next().get("count") : 0;

            System.out.println("\n✅ Relations DECLARES de Calculator: " + declaresCount);
            System.out.println("   (attendu: 4 = 3 méthodes + 1 field)");

            if (declaresCount == 0) {
                System.err.println("\n❌ PROBLÈME: Aucune relation DECLARES trouvée!");
                System.err.println("   Ceci est le bug principal à résoudre.");

                // Debug supplémentaire
                Result classCheck = tx.execute(
                    "MATCH (c:Class {name: 'Calculator'}) " +
                    "RETURN c.fqn as fqn, c.name as name"
                );
                if (classCheck.hasNext()) {
                    Map<String, Object> row = classCheck.next();
                    System.err.println("\n   Classe trouvée:");
                    System.err.println("   - name: " + row.get("name"));
                    System.err.println("   - fqn: " + row.get("fqn"));
                }

                Result funcCheck = tx.execute(
                    "MATCH (f:Function) WHERE f.fqn STARTS WITH 'com.example.Calculator.' " +
                    "RETURN f.name as name, f.fqn as fqn LIMIT 3"
                );
                System.err.println("\n   Fonctions trouvées:");
                while (funcCheck.hasNext()) {
                    Map<String, Object> row = funcCheck.next();
                    System.err.println("   - " + row.get("name") + " (" + row.get("fqn") + ")");
                }

                fail("Aucune relation DECLARES trouvée - c'est le bug à corriger");
            }

            assertTrue(declaresCount >= 4, "Il devrait y avoir au moins 4 relations DECLARES");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(6)
    @DisplayName("Étape 6: Lister les DECLARES en détail")
    void etape6_ListerDeclares() {
        System.out.println("ÉTAPE 6: Liste détaillée des DECLARES");

        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (c:Class {name: 'Calculator'})-[:DECLARES]->(target) " +
                "RETURN labels(target)[0] as targetType, " +
                "       target.name as targetName, " +
                "       target.fqn as targetFqn " +
                "ORDER BY targetType, targetName"
            );

            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                System.out.println(String.format("  %s:%s",
                    row.get("targetType"),
                    row.get("targetName")));
                count++;
            }

            if (count == 0) {
                System.err.println("❌ Aucune relation DECLARES listée");
            } else {
                System.out.println("\n✅ " + count + " éléments déclarés par Calculator");
            }

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(7)
    @DisplayName("Étape 7: Requête RAG - Trouver la méthode 'add'")
    void etape7_RequeteRAG() {
        System.out.println("ÉTAPE 7: Requête RAG - Recherche de la méthode 'add'");

        try (Transaction tx = graphDb.beginTx()) {
            // Simulation d'une requête RAG: "Trouve la méthode qui fait des additions"
            Result result = tx.execute(
                "MATCH (c:Class)-[:DECLARES]->(f:Function {name: 'add'}) " +
                "RETURN c.name as className, " +
                "       f.name as methodName, " +
                "       f.fqn as methodFqn, " +
                "       f.signature as signature"
            );

            if (!result.hasNext()) {
                System.err.println("❌ Méthode 'add' non trouvée via DECLARES");
                fail("La requête RAG n'a pas trouvé la méthode 'add'");
            }

            Map<String, Object> row = result.next();
            System.out.println("✅ Méthode trouvée:");
            System.out.println("  Classe: " + row.get("className"));
            System.out.println("  Méthode: " + row.get("methodName"));
            System.out.println("  FQN: " + row.get("methodFqn"));
            System.out.println("  Signature: " + row.get("signature"));

            assertNotNull(row.get("className"), "Le nom de la classe devrait être présent");
            assertEquals("add", row.get("methodName"), "La méthode devrait s'appeler 'add'");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(8)
    @DisplayName("Étape 8: Requête RAG - Navigation dans le graphe")
    void etape8_NavigationGraphe() {
        System.out.println("ÉTAPE 8: Navigation dans le graphe - Trouver toutes les méthodes de Calculator");

        try (Transaction tx = graphDb.beginTx()) {
            // Requête: Partir du package, trouver la classe, lister ses méthodes
            Result result = tx.execute(
                "MATCH (pkg:Package {name: 'com.example'})-[:CONTAINS]->(c:Class {name: 'Calculator'}) " +
                "OPTIONAL MATCH (c)-[:DECLARES]->(f:Function) " +
                "RETURN c.name as className, " +
                "       collect(f.name) as methods, " +
                "       count(f) as methodCount"
            );

            if (!result.hasNext()) {
                System.err.println("❌ Navigation échouée - Package ou Classe non trouvée");
                fail("La navigation dans le graphe a échoué");
            }

            Map<String, Object> row = result.next();
            long methodCount = (Long) row.get("methodCount");

            System.out.println("✅ Navigation réussie:");
            System.out.println("  Classe: " + row.get("className"));
            System.out.println("  Nombre de méthodes: " + methodCount);
            System.out.println("  Méthodes: " + row.get("methods"));

            assertTrue(methodCount >= 3, "Il devrait y avoir au moins 3 méthodes");

            tx.commit();
        }
        System.out.println();
    }

    @Test
    @Order(9)
    @DisplayName("Étape 9: Statistiques finales")
    void etape9_Statistiques() {
        System.out.println("ÉTAPE 9: Statistiques finales du graphe");

        try (Transaction tx = graphDb.beginTx()) {
            System.out.println("\n📊 STATISTIQUES COMPLÈTES:");

            // Nœuds
            String[] labels = {"Class", "Function", "Constructor", "Property", "Package", "Parameter"};
            System.out.println("\nNœuds:");
            for (String label : labels) {
                Result result = tx.execute("MATCH (n:" + label + ") RETURN count(n) as count");
                if (result.hasNext()) {
                    long count = (Long) result.next().get("count");
                    if (count > 0) {
                        System.out.println("  " + label + ": " + count);
                    }
                }
            }

            // Relations
            String[] relTypes = {"DECLARES", "CONTAINS", "RETURNS", "HAS_PARAMETER", "CALLS"};
            System.out.println("\nRelations:");
            for (String relType : relTypes) {
                Result result = tx.execute("MATCH ()-[r:" + relType + "]->() RETURN count(r) as count");
                if (result.hasNext()) {
                    long count = (Long) result.next().get("count");
                    if (count > 0) {
                        System.out.println("  " + relType + ": " + count);
                    }
                }
            }

            tx.commit();
        }
        System.out.println();
    }

    @AfterAll
    void tearDown() throws IOException {
        System.out.println("=== NETTOYAGE ===");

        if (managementService != null) {
            managementService.shutdown();
            System.out.println("✅ Connexion Neo4j fermée");
        }

        if (testDir != null && Files.exists(testDir)) {
            Files.walk(testDir)
                .sorted(Comparator.reverseOrder())
                .forEach(path -> {
                    try {
                        Files.delete(path);
                    } catch (IOException e) {
                        // Ignore
                    }
                });
            System.out.println("✅ Fichiers de test supprimés");
        }

        System.out.println("\n=== FIN DU TEST ===\n");
    }

    private void cleanDatabase() {
        try {
            Path dbPath = Paths.get(DB_PATH).toAbsolutePath().normalize();
            if (Files.exists(dbPath)) {
                System.out.println("Nettoyage de la base Neo4j: " + dbPath);
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
            Path testPath = Paths.get("test-indexation-simple");
            if (Files.exists(testPath)) {
                System.out.println("Nettoyage des fichiers de test: " + testPath);
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
