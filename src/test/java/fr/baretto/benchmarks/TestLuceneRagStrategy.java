package fr.baretto.benchmarks;

import fr.baretto.benchmarks.strategy.LuceneRagStrategy;
import org.junit.jupiter.api.*;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class TestLuceneRagStrategy {

    private Path indexDir;
    private Path sourceDir;
    private LuceneRagStrategy strategy;

    @BeforeAll
    void setup() throws Exception {
        indexDir = Files.createTempDirectory("lucene-index-test");
        sourceDir = Files.createTempDirectory("lucene-source-test");
        strategy = new LuceneRagStrategy(indexDir);

        Files.writeString(sourceDir.resolve("Calculator.java"), """
                package com.example;

                /** Utility class for arithmetic operations. */
                public class Calculator {
                    private int value;

                    public int add(int a, int b) {
                        return a + b;
                    }

                    public int multiply(int a, int b) {
                        return a * b;
                    }

                    public int getValue() {
                        return value;
                    }
                }
                """);

        Files.writeString(sourceDir.resolve("UserService.java"), """
                package com.example;

                public class UserService {
                    private String username;

                    public String authenticate(String password) {
                        return username + ":" + password;
                    }

                    public void setUsername(String username) {
                        this.username = username;
                    }
                }
                """);

        strategy.indexDirectory(sourceDir);
    }

    @AfterAll
    void tearDown() throws Exception {
        strategy.close();
        deleteDir(indexDir);
        deleteDir(sourceDir);
    }

    private void deleteDir(Path dir) throws Exception {
        if (dir != null && Files.exists(dir)) {
            Files.walk(dir).sorted(Comparator.reverseOrder())
                    .forEach(p -> { try { Files.delete(p); } catch (Exception ignored) {} });
        }
    }

    @Test
    @Order(1)
    @DisplayName("getStrategyName retourne 'Vectoriel (Lucene)'")
    void strategyName_isCorrect() {
        assertEquals("Vectoriel (Lucene)", strategy.getStrategyName());
    }

    @Test
    @Order(2)
    @DisplayName("retrieveContext retourne des résultats non vides")
    void retrieveContext_returnsResults() throws Exception {
        List<String> results = strategy.retrieveContext("arithmetic calculation");
        assertFalse(results.isEmpty());
    }

    @Test
    @Order(3)
    @DisplayName("retrieveContext est borné à TOP_K=5 résultats")
    void retrieveContext_boundedByTopK() throws Exception {
        List<String> results = strategy.retrieveContext("java method class field");
        assertTrue(results.size() <= 5);
    }

    @Test
    @Order(4)
    @DisplayName("retrieveContext trouve Calculator pour une requête arithmétique")
    void retrieveContext_findsCalculatorForArithmeticQuery() throws Exception {
        List<String> results = strategy.retrieveContext("add two numbers arithmetic");
        assertTrue(results.stream().anyMatch(r -> r.contains("Calculator")),
                "Calculator doit apparaître pour une requête arithmétique");
    }

    @Test
    @Order(5)
    @DisplayName("retrieveContext trouve UserService pour une requête d'authentification")
    void retrieveContext_findsUserServiceForAuthQuery() throws Exception {
        List<String> results = strategy.retrieveContext("user authentication password");
        assertTrue(results.stream().anyMatch(r -> r.contains("UserService") || r.contains("authenticate")),
                "UserService doit apparaître pour une requête d'authentification");
    }

    @Test
    @Order(6)
    @DisplayName("Les chunks méthode sont indexés et retrouvables")
    void retrieveContext_methodChunkIsIndexed() throws Exception {
        List<String> results = strategy.retrieveContext("multiply integers");
        assertTrue(results.stream().anyMatch(r -> r.contains("multiply")),
                "Le chunk de la méthode multiply doit être retrouvable");
    }

    @Test
    @Order(7)
    @DisplayName("La ré-indexation efface l'ancien index")
    void indexDirectory_reIndexClearsOldContent() throws Exception {
        Path newSourceDir = Files.createTempDirectory("lucene-reindex-test");
        try {
            Files.writeString(newSourceDir.resolve("PaymentService.java"), """
                    package com.example;
                    public class PaymentService {
                        public void processPayment(double amount) { }
                    }
                    """);
            strategy.indexDirectory(newSourceDir);

            List<String> results = strategy.retrieveContext("payment processing");
            assertTrue(results.stream().anyMatch(r -> r.contains("PaymentService")),
                    "Le contenu ré-indexé doit être retrouvable");

            List<String> oldResults = strategy.retrieveContext("add multiply calculator");
            assertFalse(oldResults.stream().anyMatch(r -> r.contains("Calculator")),
                    "L'ancien contenu doit être effacé après ré-indexation");
        } finally {
            // Restore
            strategy.indexDirectory(sourceDir);
            Files.walk(newSourceDir).sorted(Comparator.reverseOrder())
                    .forEach(p -> { try { Files.delete(p); } catch (Exception ignored) {} });
        }
    }

    @Test
    @Order(8)
    @DisplayName("Les fichiers Java invalides sont indexés en fallback (contenu brut)")
    void indexDirectory_handlesUnparseableFile() throws Exception {
        Path badSourceDir = Files.createTempDirectory("lucene-bad-java");
        try {
            Files.writeString(badSourceDir.resolve("Broken.java"), "this {{ is not {{ valid java");
            assertDoesNotThrow(() -> strategy.indexDirectory(badSourceDir));
        } finally {
            strategy.indexDirectory(sourceDir); // restore
            Files.walk(badSourceDir).sorted(Comparator.reverseOrder())
                    .forEach(p -> { try { Files.delete(p); } catch (Exception ignored) {} });
        }
    }

    @Test
    @Order(9)
    @DisplayName("close() peut être appelé plusieurs fois sans erreur")
    void close_isIdempotent() {
        assertDoesNotThrow(() -> {
            LuceneRagStrategy tmp = new LuceneRagStrategy(Files.createTempDirectory("lucene-close-test"));
            tmp.close();
            tmp.close();
        });
    }
}
