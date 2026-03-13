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

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests unitaires pour vérifier toutes les relations du graphe (CALLS, RETURNS, EXTENDS, etc.).
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class TestGraphRelations {

    private static final String DB_PATH = "./neo4j-db-test-relations";
    private Path testDir;
    private DatabaseManagementService managementService;
    private GraphDatabaseService graphDb;

    @BeforeAll
    void setup() throws Exception {
        cleanDatabase();

        testDir = Paths.get("test-graph-relations");
        Files.createDirectories(testDir);

        // Créer un fichier avec plusieurs patterns de relations
        String testCode = """
            package test.relations;

            public class BaseClass {
                public void baseMethod() {
                    System.out.println("Base");
                }
            }

            class ChildClass extends BaseClass {
                private String value;

                public ChildClass(String value) {
                    this.value = value;
                }

                public String getValue() {
                    return value;
                }

                public void process() {
                    baseMethod();  // CALLS à la méthode parente
                    String v = getValue();  // CALLS interne
                    System.out.println(v);
                }

                @Override
                public void baseMethod() {
                    super.baseMethod();
                }
            }

            interface IService {
                String execute();
            }

            class ServiceImpl implements IService {
                @Override
                public String execute() {
                    return "done";
                }
            }
            """;

        Path testFile = testDir.resolve("TestRelations.java");
        Files.writeString(testFile, testCode);

        Neo4jGraphRagStrategy strategy = new Neo4jGraphRagStrategy(DB_PATH);
        strategy.indexDirectory(testDir);
        strategy.shutdown();

        Path dbPath = Paths.get(DB_PATH).toAbsolutePath().normalize();
        managementService = new DatabaseManagementServiceBuilder(dbPath).build();
        graphDb = managementService.database("neo4j");
    }

    @AfterAll
    void tearDown() throws IOException {
        if (managementService != null) {
            managementService.shutdown();
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
        }
    }

    @Test
    @Order(1)
    void testExtendsRelation() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (child:Class {name: 'ChildClass'})-[:EXTENDS]->(parent:Class {name: 'BaseClass'}) " +
                "RETURN count(*) as count"
            );
            assertTrue(result.hasNext(), "La relation EXTENDS devrait exister");

            long count = (Long) result.next().get("count");
            assertEquals(1, count, "Il devrait y avoir 1 relation EXTENDS");

            tx.commit();
        }
    }

    @Test
    @Order(2)
    void testImplementsRelation() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (impl:Class {name: 'ServiceImpl'})-[:IMPLEMENTS]->(iface:Interface {name: 'IService'}) " +
                "RETURN count(*) as count"
            );
            assertTrue(result.hasNext(), "La relation IMPLEMENTS devrait exister");

            long count = (Long) result.next().get("count");
            assertEquals(1, count, "Il devrait y avoir 1 relation IMPLEMENTS");

            tx.commit();
        }
    }

    @Test
    @Order(3)
    void testCallsRelation() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (caller:Function)-[:CALLS]->(callee:Function) " +
                "WHERE caller.fqn STARTS WITH 'test.relations.' " +
                "RETURN count(*) as count"
            );
            assertTrue(result.hasNext(), "Des relations CALLS devraient exister");

            long count = (Long) result.next().get("count");
            assertTrue(count > 0, "Il devrait y avoir au moins 1 relation CALLS");

            tx.commit();
        }
    }

    @Test
    @Order(4)
    void testReturnsRelation() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (f:Function {name: 'getValue'})-[:RETURNS]->(t:Class) " +
                "RETURN t.name as returnType"
            );
            assertTrue(result.hasNext(), "La méthode getValue devrait avoir une relation RETURNS");

            String returnType = (String) result.next().get("returnType");
            assertEquals("String", returnType, "getValue devrait retourner String");

            tx.commit();
        }
    }

    @Test
    @Order(5)
    void testConstructorHasParameters() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (c:Constructor)-[:HAS_PARAMETER]->(p:Parameter) " +
                "WHERE c.fqn STARTS WITH 'test.relations.ChildClass' " +
                "RETURN count(p) as paramCount"
            );
            assertTrue(result.hasNext(), "Le constructeur devrait avoir des paramètres");

            long paramCount = (Long) result.next().get("paramCount");
            assertEquals(1, paramCount, "Le constructeur devrait avoir 1 paramètre");

            tx.commit();
        }
    }

    @Test
    @Order(6)
    void testPackageContainsClasses() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (pkg:Package {name: 'test.relations'})-[:CONTAINS]->(c:Class) " +
                "RETURN count(c) as classCount"
            );
            assertTrue(result.hasNext(), "Le package devrait contenir des classes");

            long classCount = (Long) result.next().get("classCount");
            assertTrue(classCount >= 3, "Le package devrait contenir au moins 3 classes");

            tx.commit();
        }
    }

    @Test
    @Order(7)
    void testMethodOverride() {
        try (Transaction tx = graphDb.beginTx()) {
            // Vérifier que baseMethod existe dans ChildClass
            Result result = tx.execute(
                "MATCH (c:Class {name: 'ChildClass'})-[:DECLARES]->(m:Function {name: 'baseMethod'}) " +
                "RETURN count(m) as count"
            );
            assertTrue(result.hasNext(), "baseMethod devrait être déclarée dans ChildClass");

            long count = (Long) result.next().get("count");
            assertTrue(count > 0, "ChildClass devrait déclarer baseMethod (override)");

            tx.commit();
        }
    }

    @Test
    @Order(8)
    void testInterfaceMethodDeclared() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (i:Interface {name: 'IService'})-[:DECLARES]->(m:Function {name: 'execute'}) " +
                "RETURN count(m) as count"
            );
            assertTrue(result.hasNext(), "L'interface devrait déclarer execute");

            long count = (Long) result.next().get("count");
            assertEquals(1, count, "IService devrait déclarer la méthode execute");

            tx.commit();
        }
    }

    @Test
    @Order(9)
    void testAllClassesHaveDeclares() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH (c:Class) " +
                "WHERE c.fqn STARTS WITH 'test.relations.' " +
                "OPTIONAL MATCH (c)-[:DECLARES]->(m) " +
                "WITH c, count(m) as declareCount " +
                "WHERE declareCount = 0 " +
                "RETURN c.name as className, declareCount"
            );

            assertFalse(result.hasNext(),
                "Toutes les classes devraient avoir au moins une relation DECLARES");

            tx.commit();
        }
    }

    @Test
    @Order(10)
    void testGraphStatistics() {
        try (Transaction tx = graphDb.beginTx()) {
            Result result = tx.execute(
                "MATCH ()-[r]->() " +
                "WHERE (startNode(r).fqn IS NOT NULL AND startNode(r).fqn STARTS WITH 'test.relations.') " +
                "   OR (endNode(r).fqn IS NOT NULL AND endNode(r).fqn STARTS WITH 'test.relations.') " +
                "RETURN type(r) as relType, count(r) as count " +
                "ORDER BY count DESC"
            );

            assertTrue(result.hasNext(), "Il devrait y avoir des relations");

            int totalRelations = 0;
            while (result.hasNext()) {
                var row = result.next();
                long count = (Long) row.get("count");
                totalRelations += count;
            }

            assertTrue(totalRelations > 0, "Le graphe devrait avoir des relations");

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
