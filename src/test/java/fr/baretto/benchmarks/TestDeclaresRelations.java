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
 * Tests unitaires pour vérifier que les relations DECLARES sont correctement créées.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class TestDeclaresRelations {

    private static final String DB_PATH = "./neo4j-db-test-declares";
    private Path testDir;
    private DatabaseManagementService managementService;
    private GraphDatabaseService graphDb;

    @BeforeAll
    void setup() throws Exception {
        // Nettoyer la base existante
        cleanDatabase();

        // Créer le répertoire de test
        testDir = Paths.get("test-declares-relations");
        Files.createDirectories(testDir);

        // Créer un fichier Java simple avec plusieurs méthodes
        String testCode = """
            package test.declares;

            public class TestClass {
                private String name;

                public TestClass() {
                    this.name = "default";
                }

                public String getName() {
                    return name;
                }

                public void setName(String name) {
                    this.name = name;
                }

                public void doSomething() {
                    System.out.println("Hello " + getName());
                }

                private void privateMethod() {
                    // Private method
                }
            }
            """;

        Path testFile = testDir.resolve("TestClass.java");
        Files.writeString(testFile, testCode);

        // Indexer avec Neo4jGraphRagStrategy
        Neo4jGraphRagStrategy strategy = new Neo4jGraphRagStrategy(DB_PATH);
        strategy.indexDirectory(testDir);
        strategy.shutdown();

        // Ouvrir la connexion Neo4j
        Path dbPath = Paths.get(DB_PATH).toAbsolutePath().normalize();
        managementService = new DatabaseManagementServiceBuilder(dbPath).build();
        graphDb = managementService.database("neo4j");
    }

    @AfterAll
    void tearDown() throws IOException {
        if (managementService != null) {
            managementService.shutdown();
        }

        // Nettoyer les fichiers de test
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
        }
    }

    @Test
    @Order(1)
    void testClassNodeExists() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute("MATCH (c:Class {name: 'TestClass'}) RETURN count(c) as count");
            assertTrue(result.hasNext(), "La classe TestClass devrait exister");

            long count = (Long) result.next().get("count");
            assertEquals(1, count, "Il devrait y avoir exactement 1 classe TestClass");

            tx.commit();
        }
    }

    @Test
    @Order(2)
    void testFunctionNodesExist() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (f:Function) WHERE f.fqn STARTS WITH 'test.declares.TestClass.' " +
                "RETURN count(f) as count"
            );
            assertTrue(result.hasNext(), "Des fonctions devraient exister");

            long count = (Long) result.next().get("count");
            // 1 constructeur + 4 méthodes = 5 au total
            assertTrue(count >= 4, "Il devrait y avoir au moins 4 fonctions (getName, setName, doSomething, privateMethod)");

            tx.commit();
        }
    }

    @Test
    @Order(3)
    void testDeclaresRelationsExist() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (c:Class {name: 'TestClass'})-[:DECLARES]->(f:Function) " +
                "RETURN count(f) as count"
            );
            assertTrue(result.hasNext(), "Des relations DECLARES devraient exister");

            long count = (Long) result.next().get("count");
            assertTrue(count > 0, "Il devrait y avoir au moins 1 relation DECLARES");
            assertTrue(count >= 4, "Il devrait y avoir au moins 4 relations DECLARES (une par méthode)");

            tx.commit();
        }
    }

    @Test
    @Order(4)
    void testDeclaresRelationDetails() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (c:Class {name: 'TestClass'})-[:DECLARES]->(f:Function) " +
                "RETURN f.name as methodName " +
                "ORDER BY methodName"
            );

            assertTrue(result.hasNext(), "Des relations DECLARES devraient exister");

            int count = 0;
            while (result.hasNext()) {
                Map<String, Object> row = result.next();
                String methodName = (String) row.get("methodName");
                assertNotNull(methodName, "Le nom de la méthode ne devrait pas être null");
                count++;
            }

            assertTrue(count >= 4, "Il devrait y avoir au moins 4 méthodes déclarées");

            tx.commit();
        }
    }

    @Test
    @Order(5)
    void testSpecificMethodsDeclared() {
        try (Transaction tx = graphDb.beginTx()) {
            // Vérifier que getName est déclaré
            Result result = tx.execute(
                "MATCH (c:Class {name: 'TestClass'})-[:DECLARES]->(f:Function {name: 'getName'}) " +
                "RETURN f.name as name"
            );
            assertTrue(result.hasNext(), "La méthode getName devrait être déclarée");

            // Vérifier que setName est déclaré
            result = tx.execute(
                "MATCH (c:Class {name: 'TestClass'})-[:DECLARES]->(f:Function {name: 'setName'}) " +
                "RETURN f.name as name"
            );
            assertTrue(result.hasNext(), "La méthode setName devrait être déclarée");

            // Vérifier que doSomething est déclaré
            result = tx.execute(
                "MATCH (c:Class {name: 'TestClass'})-[:DECLARES]->(f:Function {name: 'doSomething'}) " +
                "RETURN f.name as name"
            );
            assertTrue(result.hasNext(), "La méthode doSomething devrait être déclarée");

            tx.commit();
        }
    }

    @Test
    @Order(6)
    void testConstructorDeclared() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (c:Class {name: 'TestClass'})-[:DECLARES]->(ctor:Constructor) " +
                "RETURN count(ctor) as count"
            );
            assertTrue(result.hasNext(), "Un constructeur devrait être déclaré");

            long count = (Long) result.next().get("count");
            assertTrue(count >= 1, "Il devrait y avoir au moins 1 constructeur déclaré");

            tx.commit();
        }
    }

    @Test
    @Order(7)
    void testFieldDeclared() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (c:Class {name: 'TestClass'})-[:DECLARES]->(p:Property {name: 'name'}) " +
                "RETURN count(p) as count"
            );
            assertTrue(result.hasNext(), "Un field devrait être déclaré");

            long count = (Long) result.next().get("count");
            assertEquals(1, count, "Il devrait y avoir exactement 1 field 'name' déclaré");

            tx.commit();
        }
    }

    @Test
    @Order(8)
    void testNoOrphanFunctions() {
        try (Transaction tx = graphDb.beginTx()) {
            // Vérifier qu'aucune fonction n'est orpheline (sans DECLARES)
            Result result = tx.execute(
                "MATCH (f:Function) " +
                "WHERE f.fqn STARTS WITH 'test.declares.TestClass.' " +
                "AND NOT ()-[:DECLARES]->(f) " +
                "RETURN count(f) as orphanCount"
            );
            assertTrue(result.hasNext(), "La requête devrait retourner un résultat");

            long orphanCount = (Long) result.next().get("orphanCount");
            assertEquals(0, orphanCount, "Aucune fonction ne devrait être orpheline");

            tx.commit();
        }
    }

    private void cleanDatabase() {
        try {
            Path dbPath = Paths.get(DB_PATH);
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
            System.err.println("Erreur nettoyage: " + e.getMessage());
        }
    }
}
