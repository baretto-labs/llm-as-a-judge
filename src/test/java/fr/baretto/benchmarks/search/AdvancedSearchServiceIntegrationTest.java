package fr.baretto.benchmarks.search;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.model.ollama.OllamaChatModel;
import org.junit.jupiter.api.*;
import org.neo4j.driver.*;
import org.testcontainers.containers.Neo4jContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests d'intégration end-to-end pour AdvancedSearchService.
 * Valide que toutes les fonctionnalités GraphRAG fonctionnent ensemble :
 * - Hybrid Search (BM25 + Vector + RRF)
 * - Graph Traversal (K-hop expansion)
 * - Community Detection (clustering)
 * - LLM Reranking (affinage sémantique)
 */
@Testcontainers
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class AdvancedSearchServiceIntegrationTest {

    @Container
    private static final Neo4jContainer<?> neo4jContainer = new Neo4jContainer<>("neo4j:5.15")
        .withAdminPassword("test1234");

    private static Driver driver;
    private static EmbeddingModel embeddingModel;
    private static ChatModel llmModel;
    private static AdvancedSearchService advancedSearch;
    private static AdvancedSearchService advancedSearchNoLLM;
    private static boolean ollamaAvailable = false;

    @BeforeAll
    static void setup() {
        driver = GraphDatabase.driver(
            neo4jContainer.getBoltUrl(),
            AuthTokens.basic("neo4j", "test1234")
        );

        // Modèle d'embedding local (ONNX, pas besoin d'Ollama)
        embeddingModel = new AllMiniLmL6V2EmbeddingModel();

        // Essayer de se connecter à Ollama pour LLM
        try {
            llmModel = OllamaChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("llama3.2:1b")
                .temperature(0.3)
                .timeout(java.time.Duration.ofSeconds(30))
                .build();

            // Test de connexion
            String testResponse = llmModel.chat("Test");
            if (testResponse != null && !testResponse.isEmpty()) {
                ollamaAvailable = true;
                System.out.println("✅ Ollama disponible pour tests LLM Reranking");
            }
        } catch (Exception e) {
            System.out.println("⚠️  Ollama non disponible: " + e.getMessage());
            System.out.println("   Tests LLM Reranking seront skippés");
        }

        // Créer le graphe de test
        createTestGraph();

        // Créer les index Neo4j
        createIndexes();

        // Indexer les embeddings
        indexEmbeddings();

        // Initialiser les services
        if (ollamaAvailable) {
            advancedSearch = new AdvancedSearchService(driver, embeddingModel, llmModel);
        }
        advancedSearchNoLLM = new AdvancedSearchService(driver, embeddingModel);
    }

    @AfterAll
    static void tearDown() {
        if (driver != null) {
            driver.close();
        }
    }

    /**
     * Crée un graphe de test avec 2 modules distincts :
     * - Module Authentication (AuthService, UserRepository, TokenManager)
     * - Module Payment (PaymentGateway, TransactionLog, InvoiceService)
     */
    private static void createTestGraph() {
        try (Session session = driver.session()) {
            // === MODULE AUTHENTICATION ===

            // AuthenticationService
            session.run("""
                CREATE (c:Class {
                    name: 'AuthenticationService',
                    fqn: 'com.example.auth.AuthenticationService',
                    javaDoc: 'Service for user authentication with JWT tokens and session management'
                })
                """);

            session.run("""
                CREATE (m:Method {
                    name: 'authenticate',
                    fqn: 'com.example.auth.AuthenticationService.authenticate',
                    signature: 'User authenticate(String username, String password)',
                    javaDoc: 'Authenticates a user with username and password. Returns User object if credentials are valid.'
                })
                """);

            // UserRepository
            session.run("""
                CREATE (c:Class {
                    name: 'UserRepository',
                    fqn: 'com.example.auth.UserRepository',
                    javaDoc: 'Repository for user data persistence and retrieval from database'
                })
                """);

            session.run("""
                CREATE (m:Method {
                    name: 'findByUsername',
                    fqn: 'com.example.auth.UserRepository.findByUsername',
                    signature: 'User findByUsername(String username)',
                    javaDoc: 'Finds a user by their username in the database'
                })
                """);

            // TokenManager
            session.run("""
                CREATE (c:Class {
                    name: 'TokenManager',
                    fqn: 'com.example.auth.TokenManager',
                    javaDoc: 'Manages JWT token generation and validation for authentication'
                })
                """);

            session.run("""
                CREATE (m:Method {
                    name: 'generateToken',
                    fqn: 'com.example.auth.TokenManager.generateToken',
                    signature: 'String generateToken(User user)',
                    javaDoc: 'Generates a JWT token for the given user'
                })
                """);

            // === MODULE PAYMENT ===

            // PaymentGateway
            session.run("""
                CREATE (c:Class {
                    name: 'PaymentGateway',
                    fqn: 'com.example.payment.PaymentGateway',
                    javaDoc: 'Gateway for processing payments through Stripe API'
                })
                """);

            session.run("""
                CREATE (m:Method {
                    name: 'processPayment',
                    fqn: 'com.example.payment.PaymentGateway.processPayment',
                    signature: 'PaymentResult processPayment(Payment payment)',
                    javaDoc: 'Processes a payment transaction using Stripe payment gateway'
                })
                """);

            // TransactionLog
            session.run("""
                CREATE (c:Class {
                    name: 'TransactionLog',
                    fqn: 'com.example.payment.TransactionLog',
                    javaDoc: 'Logs all payment transactions for audit and tracking'
                })
                """);

            session.run("""
                CREATE (m:Method {
                    name: 'logTransaction',
                    fqn: 'com.example.payment.TransactionLog.logTransaction',
                    signature: 'void logTransaction(PaymentResult result)',
                    javaDoc: 'Logs a completed payment transaction'
                })
                """);

            // InvoiceService
            session.run("""
                CREATE (c:Class {
                    name: 'InvoiceService',
                    fqn: 'com.example.payment.InvoiceService',
                    javaDoc: 'Service for generating and managing invoices'
                })
                """);

            session.run("""
                CREATE (m:Method {
                    name: 'generateInvoice',
                    fqn: 'com.example.payment.InvoiceService.generateInvoice',
                    signature: 'Invoice generateInvoice(Payment payment)',
                    javaDoc: 'Generates an invoice for a completed payment'
                })
                """);

            // === RELATIONS INTRA-MODULE AUTH ===

            session.run("""
                MATCH (auth:Class {name: 'AuthenticationService'}),
                      (authMethod:Method {name: 'authenticate'})
                CREATE (auth)-[:DECLARES]->(authMethod)
                """);

            session.run("""
                MATCH (repo:Class {name: 'UserRepository'}),
                      (findMethod:Method {name: 'findByUsername'})
                CREATE (repo)-[:DECLARES]->(findMethod)
                """);

            session.run("""
                MATCH (token:Class {name: 'TokenManager'}),
                      (genMethod:Method {name: 'generateToken'})
                CREATE (token)-[:DECLARES]->(genMethod)
                """);

            session.run("""
                MATCH (authMethod:Method {name: 'authenticate'}),
                      (findMethod:Method {name: 'findByUsername'})
                CREATE (authMethod)-[:CALLS]->(findMethod)
                """);

            session.run("""
                MATCH (authMethod:Method {name: 'authenticate'}),
                      (genMethod:Method {name: 'generateToken'})
                CREATE (authMethod)-[:CALLS]->(genMethod)
                """);

            // === RELATIONS INTRA-MODULE PAYMENT ===

            session.run("""
                MATCH (gateway:Class {name: 'PaymentGateway'}),
                      (processMethod:Method {name: 'processPayment'})
                CREATE (gateway)-[:DECLARES]->(processMethod)
                """);

            session.run("""
                MATCH (log:Class {name: 'TransactionLog'}),
                      (logMethod:Method {name: 'logTransaction'})
                CREATE (log)-[:DECLARES]->(logMethod)
                """);

            session.run("""
                MATCH (invoice:Class {name: 'InvoiceService'}),
                      (genInvoiceMethod:Method {name: 'generateInvoice'})
                CREATE (invoice)-[:DECLARES]->(genInvoiceMethod)
                """);

            session.run("""
                MATCH (processMethod:Method {name: 'processPayment'}),
                      (logMethod:Method {name: 'logTransaction'})
                CREATE (processMethod)-[:CALLS]->(logMethod)
                """);

            session.run("""
                MATCH (processMethod:Method {name: 'processPayment'}),
                      (genInvoiceMethod:Method {name: 'generateInvoice'})
                CREATE (processMethod)-[:CALLS]->(genInvoiceMethod)
                """);

            System.out.println("✅ Graphe de test créé avec 2 modules:");
            System.out.println("   Module Auth: 3 classes, 3 méthodes");
            System.out.println("   Module Payment: 3 classes, 3 méthodes");
        }
    }

    /**
     * Crée les index Full-Text et Vector nécessaires.
     */
    private static void createIndexes() {
        try (Session session = driver.session()) {
            // Index Full-Text pour recherche lexicale (un par label - Neo4j 5.x ne supporte pas le pipe)
            runIgnoreError(session, "CREATE FULLTEXT INDEX codeFullText IF NOT EXISTS FOR (n:Class) ON EACH [n.name, n.javaDoc]");
            runIgnoreError(session, "CREATE FULLTEXT INDEX codeFullTextMethod IF NOT EXISTS FOR (n:Method) ON EACH [n.name, n.javaDoc]");

            // Index Vector pour recherche sémantique (dimension 384 pour AllMiniLmL6V2)
            runIgnoreError(session, """
                CREATE VECTOR INDEX codeVector IF NOT EXISTS
                FOR (n:Class) ON n.embedding
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 384,
                    `vector.similarity_function`: 'cosine'
                }}
                """);
            runIgnoreError(session, """
                CREATE VECTOR INDEX codeVectorMethod IF NOT EXISTS
                FOR (n:Method) ON n.embedding
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 384,
                    `vector.similarity_function`: 'cosine'
                }}
                """);

            // Attendre que les index soient en ligne
            Thread.sleep(2000);

            System.out.println("✅ Index Neo4j créés");
        } catch (Exception e) {
            System.err.println("⚠️  Erreur création index: " + e.getMessage());
        }
    }

    private static void runIgnoreError(Session session, String cypher) {
        try {
            session.run(cypher);
        } catch (Exception e) {
            System.err.println("⚠️  Index creation warning: " + e.getMessage());
        }
    }

    /**
     * Indexe les embeddings pour tous les nœuds.
     */
    private static void indexEmbeddings() {
        try (Session session = driver.session()) {
            Result result = session.run("MATCH (n) WHERE n:Class OR n:Method RETURN id(n) as nodeId, n.name as name, n.javaDoc as javaDoc");

            result.stream().forEach(record -> {
                long nodeId = record.get("nodeId").asLong();
                String name = record.get("name").asString("");
                String javaDoc = record.get("javaDoc").asString("");

                // Créer le texte à embedder
                String text = name + " " + javaDoc;

                // Générer l'embedding
                float[] embedding = embeddingModel.embed(text).content().vector();

                // Stocker dans Neo4j
                session.run(
                    "MATCH (n) WHERE id(n) = $nodeId SET n.embedding = $embedding",
                    Map.of("nodeId", nodeId, "embedding", embedding)
                );
            });

            System.out.println("✅ Embeddings indexés");
        }
    }

    @Test
    @Order(1)
    @DisplayName("Test 1: Recherche hybride basique sans LLM")
    void test1_BasicHybridSearch() throws SearchException {
        List<EntryPoint> results = advancedSearchNoLLM.findEntryPoints("authenticate user", 5);

        assertFalse(results.isEmpty(), "Devrait trouver des résultats");
        System.out.println("\n📊 Résultats recherche hybride 'authenticate user':");
        for (int i = 0; i < results.size(); i++) {
            EntryPoint entry = results.get(i);
            System.out.println(String.format("  %d. %s (%s) - score: %.4f",
                i + 1, entry.name(), entry.nodeType(), entry.score()));
        }

        // Le top résultat devrait être lié à l'authentication
        String topName = results.get(0).name().toLowerCase();
        assertTrue(topName.contains("auth") || topName.contains("user"),
            "Le top résultat devrait être lié à authentication");
    }

    @Test
    @Order(2)
    @DisplayName("Test 2: Recherche hybride avec expansion graphe")
    void test2_HybridSearchWithGraphExpansion() throws SearchException {
        // Service avec graph expansion activée (1 hop)
        AdvancedSearchService serviceWithExpansion = new AdvancedSearchService(
            driver, embeddingModel, null, true, false, 1
        );

        List<EntryPoint> results = serviceWithExpansion.findEntryPoints("authenticate", 10);

        assertFalse(results.isEmpty(), "Devrait trouver des résultats");
        System.out.println("\n📊 Résultats avec expansion graphe (1 hop):");
        for (int i = 0; i < Math.min(5, results.size()); i++) {
            EntryPoint entry = results.get(i);
            System.out.println(String.format("  %d. %s (%s)",
                i + 1, entry.name(), entry.nodeType()));
        }

        // Avec expansion, devrait trouver plus de résultats
        assertTrue(results.size() >= 3, "L'expansion devrait ajouter des résultats");
    }

    @Test
    @Order(3)
    @DisplayName("Test 3: Recherche hybride avec LLM reranking (si disponible)")
    void test3_HybridSearchWithLLMReranking() throws SearchException {
        if (!ollamaAvailable) {
            System.out.println("⏭️  Test skippé (Ollama non disponible)");
            return;
        }

        List<EntryPoint> results = advancedSearch.findEntryPoints("authenticate user with password", 5);

        assertFalse(results.isEmpty(), "Devrait trouver des résultats");
        System.out.println("\n📊 Résultats avec LLM reranking:");
        for (int i = 0; i < results.size(); i++) {
            EntryPoint entry = results.get(i);
            System.out.println(String.format("  %d. %s (%s) - %s",
                i + 1, entry.name(), entry.nodeType(), entry.fqn()));
        }

        // Le top résultat devrait être très pertinent (authenticate method)
        String topName = results.get(0).name().toLowerCase();
        assertTrue(topName.contains("auth") || topName.contains("user"),
            "Le top résultat devrait être très pertinent après LLM reranking");
    }

    @Test
    @Order(4)
    @DisplayName("Test 4: Recherche globale par communautés (module authentication)")
    void test4_CommunitySearchAuth() throws SearchException {
        List<CommunityDetection.Community> communities = advancedSearchNoLLM.findCommunities(
            "authentication",
            3
        );

        assertFalse(communities.isEmpty(), "Devrait trouver au moins 1 communauté");

        System.out.println("\n📊 Communautés trouvées pour 'authentication':");
        for (CommunityDetection.Community community : communities) {
            System.out.println(String.format("  • %s (size=%d)",
                community.name(), community.size()));
            System.out.println("    Classes: " +
                community.getClasses().stream()
                    .map(CommunityDetection.CommunityNode::name)
                    .toList());
        }

        // La première communauté devrait contenir AuthenticationService
        CommunityDetection.Community topCommunity = communities.get(0);
        boolean hasAuthService = topCommunity.getClasses().stream()
            .anyMatch(node -> node.name().contains("Authentication"));
        assertTrue(hasAuthService, "La communauté devrait contenir AuthenticationService");
    }

    @Test
    @Order(5)
    @DisplayName("Test 5: Recherche globale par communautés (module payment)")
    void test5_CommunitySearchPayment() throws SearchException {
        List<CommunityDetection.Community> communities = advancedSearchNoLLM.findCommunities(
            "payment processing",
            3
        );

        if (!communities.isEmpty()) {
            System.out.println("\n📊 Communautés trouvées pour 'payment processing':");
            for (CommunityDetection.Community community : communities) {
                System.out.println(String.format("  • %s (size=%d)",
                    community.name(), community.size()));
                System.out.println("    Classes: " +
                    community.getClasses().stream()
                        .map(CommunityDetection.CommunityNode::name)
                        .toList());
            }

            // Vérifier qu'on a des classes liées au payment
            boolean hasPaymentClasses = communities.stream()
                .flatMap(c -> c.getClasses().stream())
                .anyMatch(node -> node.name().toLowerCase().contains("payment") ||
                                  node.name().toLowerCase().contains("invoice"));
            assertTrue(hasPaymentClasses, "Devrait trouver des classes de payment");
        }
    }

    @Test
    @Order(6)
    @DisplayName("Test 6: Conversion communauté → EntryPoints")
    void test6_CommunityToEntryPoints() throws SearchException {
        List<CommunityDetection.Community> communities = advancedSearchNoLLM.findCommunities(
            "authentication",
            1
        );

        assertFalse(communities.isEmpty(), "Devrait trouver au moins 1 communauté");

        CommunityDetection.Community community = communities.get(0);
        List<EntryPoint> entryPoints = advancedSearchNoLLM.communityToEntryPoints(community, 5);

        assertFalse(entryPoints.isEmpty(), "Devrait convertir en EntryPoints");
        System.out.println("\n📊 EntryPoints de la communauté " + community.name() + ":");
        for (EntryPoint entry : entryPoints) {
            System.out.println(String.format("  • %s (%s) - %s",
                entry.name(), entry.nodeType(), entry.fqn()));
        }

        // Devrait avoir principalement des classes en premier
        long classCount = entryPoints.stream()
            .filter(ep -> ep.nodeType().equals("Class"))
            .count();
        assertTrue(classCount > 0, "Devrait avoir des classes dans les EntryPoints");
    }

    @Test
    @Order(7)
    @DisplayName("Test 7: Trouver chemins entre nœuds")
    void test7_FindPathsBetween() throws SearchException {
        try (Session session = driver.session()) {
            // Trouver les IDs de authenticate et logTransaction
            Result authResult = session.run(
                "MATCH (m:Method {name: 'authenticate'}) RETURN id(m) as nodeId"
            );
            if (!authResult.hasNext()) {
                System.out.println("⏭️  Test skippé (nœud authenticate non trouvé)");
                return;
            }
            long authenticateId = authResult.single().get("nodeId").asLong();

            Result logResult = session.run(
                "MATCH (m:Method {name: 'logTransaction'}) RETURN id(m) as nodeId"
            );
            if (!logResult.hasNext()) {
                System.out.println("⏭️  Test skippé (nœud logTransaction non trouvé)");
                return;
            }
            long logTransactionId = logResult.single().get("nodeId").asLong();

            // Chercher chemins (ne devrait pas en trouver car modules distincts)
            List<GraphTraversal.GraphPath> paths = advancedSearchNoLLM.findPathsBetween(
                authenticateId,
                logTransactionId,
                4
            );

            System.out.println("\n📊 Chemins entre authenticate et logTransaction:");
            System.out.println("  Chemins trouvés: " + paths.size());

            if (paths.isEmpty()) {
                System.out.println("  (Normal: modules distincts sans connexion)");
            }
        }
    }

    @Test
    @Order(8)
    @DisplayName("Test 8: Extraire contexte graphe autour d'un nœud")
    void test8_ExtractContext() throws SearchException {
        try (Session session = driver.session()) {
            // Trouver AuthenticationService
            Result result = session.run(
                "MATCH (c:Class {name: 'AuthenticationService'}) RETURN id(c) as nodeId"
            );
            if (!result.hasNext()) {
                System.out.println("⏭️  Test skippé (AuthenticationService non trouvé)");
                return;
            }
            long authServiceId = result.single().get("nodeId").asLong();

            EntryPoint authService = new EntryPoint(
                authServiceId,
                "Class",
                "AuthenticationService",
                "com.example.auth.AuthenticationService",
                1.0,
                Map.of()
            );

            GraphTraversal.Subgraph subgraph = advancedSearchNoLLM.extractContext(authService, 2);

            assertFalse(subgraph.nodes().isEmpty(), "Le sous-graphe ne devrait pas être vide");
            System.out.println("\n📊 Contexte autour de AuthenticationService (radius=2):");
            System.out.println("  Nœuds dans le contexte: " + subgraph.nodes().size());

            List<GraphTraversal.SubgraphNode> sortedNodes = subgraph.sortedByScore();
            System.out.println("  Top 5 nœuds par score:");
            for (int i = 0; i < Math.min(5, sortedNodes.size()); i++) {
                GraphTraversal.SubgraphNode node = sortedNodes.get(i);
                System.out.println(String.format("    %d. %s (distance=%d, score=%.4f)",
                    i + 1, node.name(), node.distance(), node.score()));
            }
        }
    }

    @Test
    @Order(9)
    @DisplayName("Test 9: Statistiques du service")
    void test9_ServiceStats() {
        Map<String, Object> stats = advancedSearchNoLLM.getStats();

        assertNotNull(stats, "Les stats ne devraient pas être null");
        assertTrue((Boolean) stats.get("graphExpansionEnabled"),
            "Graph expansion devrait être activé par défaut");
        assertFalse((Boolean) stats.get("llmRerankingEnabled"),
            "LLM reranking devrait être désactivé (pas de LLM)");

        System.out.println("\n📊 Statistiques du service:");
        stats.forEach((key, value) ->
            System.out.println(String.format("  • %s: %s", key, value)));

        if (ollamaAvailable) {
            Map<String, Object> statsWithLLM = advancedSearch.getStats();
            assertTrue((Boolean) statsWithLLM.get("llmRerankingEnabled"),
                "LLM reranking devrait être activé si LLM disponible");
        }
    }

    @Test
    @Order(10)
    @DisplayName("Test 10: Pipeline complet (Hybrid + Graph + LLM)")
    void test10_FullPipeline() throws SearchException {
        if (!ollamaAvailable) {
            System.out.println("⏭️  Test skippé (Ollama non disponible)");
            return;
        }

        System.out.println("\n🚀 Test du pipeline complet:");

        // 1. Recherche hybride de base
        System.out.println("\n1️⃣  Hybrid Search (BM25 + Vector + RRF):");
        HybridSearchService basicHybrid = new HybridSearchService(driver, embeddingModel);
        List<EntryPoint> hybridResults = basicHybrid.findEntryPoints("user authentication", 3);
        System.out.println("   Résultats: " + hybridResults.size());
        hybridResults.forEach(ep -> System.out.println("   • " + ep.name()));

        // 2. + Graph Expansion
        System.out.println("\n2️⃣  + Graph Expansion (1 hop):");
        AdvancedSearchService withGraph = new AdvancedSearchService(
            driver, embeddingModel, null, true, false, 1
        );
        List<EntryPoint> expandedResults = withGraph.findEntryPoints("user authentication", 5);
        System.out.println("   Résultats: " + expandedResults.size());
        System.out.println("   (Augmentation: +" + (expandedResults.size() - hybridResults.size()) + " nœuds)");

        // 3. + LLM Reranking
        System.out.println("\n3️⃣  + LLM Reranking:");
        List<EntryPoint> finalResults = advancedSearch.findEntryPoints("user authentication", 5);
        System.out.println("   Résultats finaux: " + finalResults.size());
        System.out.println("   Top 3:");
        for (int i = 0; i < Math.min(3, finalResults.size()); i++) {
            System.out.println(String.format("   %d. %s (%s)",
                i + 1, finalResults.get(i).name(), finalResults.get(i).nodeType()));
        }

        // 4. Recherche globale par communauté
        System.out.println("\n4️⃣  Community-based Global Search:");
        List<CommunityDetection.Community> communities = advancedSearch.findCommunities(
            "authentication",
            2
        );
        System.out.println("   Communautés trouvées: " + communities.size());
        if (!communities.isEmpty()) {
            CommunityDetection.Community topCommunity = communities.get(0);
            System.out.println("   Top communauté: " + topCommunity.name() +
                " (size=" + topCommunity.size() + ")");
        }

        assertFalse(finalResults.isEmpty(), "Le pipeline complet devrait retourner des résultats");
    }
}
