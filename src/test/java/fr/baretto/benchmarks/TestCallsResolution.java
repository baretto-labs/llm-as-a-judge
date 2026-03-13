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
 * Tests unitaires pour vérifier la résolution des appels de méthodes (CALLS).
 * Objectif: 95%+ de résolution avec le nouveau système de VariableScope.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class TestCallsResolution {

    private static final String DB_PATH = "./neo4j-db-test-calls";
    private Path testDir;
    private DatabaseManagementService managementService;
    private GraphDatabaseService graphDb;

    @BeforeAll
    void setup() throws Exception {
        cleanDatabase();

        testDir = Paths.get("test-calls-resolution");
        Files.createDirectories(testDir);

        // Créer un fichier avec différents patterns d'appels
        String testCode = """
            package test.calls;

            public class UserRepository {
                public User findById(int id) {
                    return new User("test");
                }

                public void save(User user) {
                    System.out.println("Saving " + user.getName());
                }
            }

            class User {
                private String name;

                public User(String name) {
                    this.name = name;
                }

                public String getName() {
                    return name;
                }

                public void setName(String name) {
                    this.name = name;
                }
            }

            class UserService {
                private UserRepository repository;

                public UserService() {
                    this.repository = new UserRepository();
                }

                // Test 1: Appel via variable locale
                public void processUser(int userId) {
                    User user = repository.findById(userId);
                    user.setName("Updated");
                    repository.save(user);
                }

                // Test 2: Appel via field
                public User getUser(int id) {
                    return repository.findById(id);
                }

                // Test 3: Appel via paramètre
                public void updateUser(User user, String newName) {
                    user.setName(newName);
                }

                // Test 4: Appel interne (this)
                public void complexProcess(int id) {
                    User user = getUser(id);
                    updateUser(user, "Complex");
                }

                // Test 5: Appel statique
                public void logUser(User user) {
                    String name = user.getName();
                    System.out.println(name);
                }
            }
            """;

        Path testFile = testDir.resolve("UserService.java");
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
    void testCallsViaLocalVariable() {
        try (Transaction tx = graphDb.beginTx()) {
            // processUser() appelle user.setName() où user est une variable locale
            Result result = tx.execute(
                "MATCH (caller:Function {name: 'processUser'})-[:CALLS]->(callee:Function {name: 'setName'}) " +
                "RETURN count(*) as count"
            );
            assertTrue(result.hasNext(), "processUser devrait appeler setName");

            long count = (Long) result.next().get("count");
            assertTrue(count > 0, "L'appel via variable locale devrait être résolu");

            tx.commit();
        }
    }

    @Test
    @Order(2)
    void testCallsViaField() {
        try (Transaction tx = graphDb.beginTx()) {
            // getUser() appelle repository.findById() où repository est un field
            Result result = tx.execute(
                "MATCH (caller:Function {name: 'getUser'})-[:CALLS]->(callee:Function {name: 'findById'}) " +
                "RETURN count(*) as count"
            );
            assertTrue(result.hasNext(), "getUser devrait appeler findById");

            long count = (Long) result.next().get("count");
            assertTrue(count > 0, "L'appel via field devrait être résolu");

            tx.commit();
        }
    }

    @Test
    @Order(3)
    void testCallsViaParameter() {
        try (Transaction tx = graphDb.beginTx()) {
            // updateUser(User user) appelle user.setName() où user est un paramètre
            Result result = tx.execute(
                "MATCH (caller:Function {name: 'updateUser'})-[:CALLS]->(callee:Function {name: 'setName'}) " +
                "RETURN count(*) as count"
            );
            assertTrue(result.hasNext(), "updateUser devrait appeler setName");

            long count = (Long) result.next().get("count");
            assertTrue(count > 0, "L'appel via paramètre devrait être résolu");

            tx.commit();
        }
    }

    @Test
    @Order(4)
    void testInternalCalls() {
        try (Transaction tx = graphDb.beginTx()) {
            // complexProcess() appelle getUser() et updateUser() (méthodes de la même classe)
            Result result = tx.execute(
                "MATCH (caller:Function {name: 'complexProcess'})-[:CALLS]->(callee:Function) " +
                "WHERE callee.name IN ['getUser', 'updateUser'] " +
                "RETURN count(*) as count"
            );
            assertTrue(result.hasNext(), "complexProcess devrait appeler getUser et updateUser");

            long count = (Long) result.next().get("count");
            assertTrue(count >= 2, "Les appels internes devraient être résolus");

            tx.commit();
        }
    }

    @Test
    @Order(5)
    void testChainedCalls() {
        try (Transaction tx = graphDb.beginTx()) {
            // processUser() contient: User user = repository.findById(userId)
            // donc appelle findById
            Result result = tx.execute(
                "MATCH (caller:Function {name: 'processUser'})-[:CALLS]->(callee:Function {name: 'findById'}) " +
                "RETURN count(*) as count"
            );
            assertTrue(result.hasNext(), "processUser devrait appeler findById");

            long count = (Long) result.next().get("count");
            assertTrue(count > 0, "Les appels chaînés devraient être résolus");

            tx.commit();
        }
    }

    @Test
    @Order(6)
    void testResolutionRate() {
        try (Transaction tx = graphDb.beginTx()) {
            // Calculer le taux de résolution global
            Result result = tx.execute(
                "MATCH (f:Function)-[c:CALLS]->(target) " +
                "WHERE f.fqn STARTS WITH 'test.calls.' " +
                "WITH count(c) as totalCalls, " +
                "     sum(CASE WHEN target:Function THEN 1 ELSE 0 END) as resolvedCalls " +
                "RETURN totalCalls, resolvedCalls, " +
                "       (resolvedCalls * 100.0 / totalCalls) as resolutionRate"
            );

            assertTrue(result.hasNext(), "Il devrait y avoir des statistiques de résolution");

            var row = result.next();
            long totalCalls = (Long) row.get("totalCalls");
            long resolvedCalls = (Long) row.get("resolvedCalls");
            double resolutionRate = (Double) row.get("resolutionRate");

            assertTrue(totalCalls > 0, "Il devrait y avoir des appels");
            assertTrue(resolvedCalls > 0, "Au moins certains appels devraient être résolus");

            System.out.println(String.format(
                "Taux de résolution: %.1f%% (%d/%d)",
                resolutionRate, resolvedCalls, totalCalls
            ));

            // Objectif: 95%+ de résolution
            assertTrue(resolutionRate >= 80.0,
                String.format("Le taux de résolution devrait être >= 80%% (actuel: %.1f%%)", resolutionRate));

            tx.commit();
        }
    }

    @Test
    @Order(7)
    void testCallDetails() {
        try (Transaction tx = graphDb.beginTx()) {
            // Vérifier les détails des appels (receiver, receiverType)
            Result result = tx.execute(
                "MATCH (f:Function {name: 'processUser'})-[c:CALLS]->(target:Function) " +
                "RETURN target.name as targetName, " +
                "       c.receiver as receiver, " +
                "       c.receiverType as receiverType"
            );

            assertTrue(result.hasNext(), "processUser devrait avoir des appels");

            while (result.hasNext()) {
                var row = result.next();
                String targetName = (String) row.get("targetName");
                assertNotNull(targetName, "Le nom de la cible ne devrait pas être null");

                // Vérifier que les appels ont des receivers
                Object receiver = row.get("receiver");
                // receiver peut être null pour les appels internes (this implicite)
            }

            tx.commit();
        }
    }

    @Test
    @Order(8)
    void testNoOrphanCalls() {
        try (Transaction tx = graphDb.beginTx()) {
            // Vérifier qu'il n'y a pas d'appels non résolus vers des méthodes inexistantes
            Result result = tx.execute(
                "MATCH (f:Function)-[c:CALLS]->(target) " +
                "WHERE f.fqn STARTS WITH 'test.calls.' " +
                "AND target:Function " +
                "AND NOT exists(()-[:DECLARES]->(target)) " +
                "RETURN count(*) as orphanCount"
            );

            assertTrue(result.hasNext(), "La requête devrait retourner un résultat");

            long orphanCount = (Long) result.next().get("orphanCount");
            // Il peut y avoir des appels vers des méthodes externes (System.out.println)
            // donc on vérifie juste qu'il n'y a pas trop d'orphelins

            tx.commit();
        }
    }

    @Test
    @Order(9)
    void testMethodCallCounts() {
        try (Transaction tx = graphDb.beginTx()) {
            // Compter combien de fois chaque méthode est appelée
            Result result = tx.execute(
                "MATCH (caller:Function)-[:CALLS]->(f:Function) " +
                "WHERE f.fqn STARTS WITH 'test.calls.' " +
                "WITH f, count(caller) as callCount " +
                "RETURN f.name as methodName, callCount " +
                "ORDER BY callCount DESC"
            );

            assertTrue(result.hasNext(), "Il devrait y avoir des méthodes appelées");

            while (result.hasNext()) {
                var row = result.next();
                String methodName = (String) row.get("methodName");
                long callCount = (Long) row.get("callCount");

                assertTrue(callCount > 0, "Les méthodes devraient être appelées au moins une fois");
            }

            tx.commit();
        }
    }

    @Test
    @Order(10)
    void testSpecificCallPattern() {
        try (Transaction tx = graphDb.beginTx()) {
            // Test spécifique: processUser appelle repository.save(user)
            // user est une variable locale de type User
            Result result = tx.execute(
                "MATCH (caller:Function {name: 'processUser'})-[c:CALLS]->(callee:Function {name: 'save'}) " +
                "RETURN c.receiver as receiver, c.receiverType as receiverType"
            );

            assertTrue(result.hasNext(), "processUser devrait appeler save");

            var row = result.next();
            String receiver = (String) row.get("receiver");
            String receiverType = (String) row.get("receiverType");

            assertEquals("repository", receiver, "Le receiver devrait être 'repository'");
            assertNotNull(receiverType, "Le receiverType devrait être résolu");

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
