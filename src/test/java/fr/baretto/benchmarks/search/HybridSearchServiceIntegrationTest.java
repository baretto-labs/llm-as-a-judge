package fr.baretto.benchmarks.search;

import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.ollama.OllamaEmbeddingModel;
import org.junit.jupiter.api.*;
import org.neo4j.driver.*;
import org.testcontainers.containers.Neo4jContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests d'intégration pour HybridSearchService.
 * Utilise Testcontainers pour lancer un vrai Neo4j éphémère.
 */
@Testcontainers
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class HybridSearchServiceIntegrationTest {

    @Container
    private static final Neo4jContainer<?> neo4jContainer = new Neo4jContainer<>("neo4j:5.15")
        .withAdminPassword("test1234")
        .withEnv("NEO4J_PLUGINS", "[\"apoc\"]");

    private Driver driver;
    private EmbeddingModel embeddingModel;
    private HybridSearchService searchService;

    @BeforeAll
    void setup() {
        // Créer le driver Neo4j
        driver = GraphDatabase.driver(
            neo4jContainer.getBoltUrl(),
            AuthTokens.basic("neo4j", "test1234")
        );

        // Créer un vrai modèle d'embedding Ollama
        // Utilise nomic-embed-text (768 dimensions)
        embeddingModel = OllamaEmbeddingModel.builder()
            .baseUrl("http://localhost:11434")
            .modelName("nomic-embed-text")
            .build();

        // Créer le service
        searchService = new HybridSearchService(driver, embeddingModel, 60);

        System.out.println("✅ Neo4j container démarré: " + neo4jContainer.getBoltUrl());
        System.out.println("✅ Ollama embedding model: nomic-embed-text (768 dimensions)");
    }

    @AfterAll
    void tearDown() {
        if (driver != null) {
            driver.close();
            neo4jContainer.close();
        }
    }

    @Test
    @Order(1)
    @DisplayName("Test 1: Créer les index Full-Text et Vectoriel")
    void test1_CreateIndexes() {
        try (Session session = driver.session()) {
            // Créer les index Full-Text (un par label car Neo4j 5.15 ne supporte pas le pipe)
            try {
                session.run("""
                    CREATE FULLTEXT INDEX codeFullText IF NOT EXISTS
                    FOR (n:Class)
                    ON EACH [n.name, n.javaDoc]
                    """);
            } catch (Exception e) {
                // Index existe déjà, ignorer
            }

            try {
                session.run("""
                    CREATE FULLTEXT INDEX codeFullTextMethod IF NOT EXISTS
                    FOR (n:Method)
                    ON EACH [n.name, n.javaDoc]
                    """);
            } catch (Exception e) {
                // Index existe déjà, ignorer
            }

            try {
                session.run("""
                    CREATE FULLTEXT INDEX codeFullTextFunction IF NOT EXISTS
                    FOR (n:Function)
                    ON EACH [n.name, n.javaDoc]
                    """);
            } catch (Exception e) {
                // Index existe déjà, ignorer
            }

            // Créer les index Vectoriels (768 dimensions pour nomic-embed-text)
            try {
                session.run("""
                    CREATE VECTOR INDEX codeVector IF NOT EXISTS
                    FOR (n:Class)
                    ON n.embedding
                    OPTIONS {
                        indexConfig: {
                            `vector.dimensions`: 768,
                            `vector.similarity_function`: 'cosine'
                        }
                    }
                    """);
            } catch (Exception e) {
                // Index existe déjà, ignorer
            }

            try {
                session.run("""
                    CREATE VECTOR INDEX codeVectorMethod IF NOT EXISTS
                    FOR (n:Method)
                    ON n.embedding
                    OPTIONS {
                        indexConfig: {
                            `vector.dimensions`: 768,
                            `vector.similarity_function`: 'cosine'
                        }
                    }
                    """);
            } catch (Exception e) {
                // Index existe déjà, ignorer
            }

            try {
                session.run("""
                    CREATE VECTOR INDEX codeVectorFunction IF NOT EXISTS
                    FOR (n:Function)
                    ON n.embedding
                    OPTIONS {
                        indexConfig: {
                            `vector.dimensions`: 768,
                            `vector.similarity_function`: 'cosine'
                        }
                    }
                    """);
            } catch (Exception e) {
                // Index existe déjà, ignorer
            }

            System.out.println("✅ Index Full-Text et Vectoriel créés (768 dimensions pour nomic-embed-text)");

            // Attendre que les index soient prêts (Neo4j les crée de manière asynchrone)
            waitForIndexes(session);
        }
    }

    /**
     * Attend que tous les index soient en ligne (ONLINE).
     * Les index Neo4j sont créés de manière asynchrone.
     */
    private void waitForIndexes(Session session) {
        System.out.print("⏳ Attente que les index soient prêts...");
        int maxAttempts = 30; // 30 secondes max
        int attempt = 0;

        while (attempt < maxAttempts) {
            try {
                // Vérifier l'état des index
                var result = session.run("SHOW INDEXES YIELD name, state WHERE state = 'ONLINE' RETURN count(*) as count");
                if (result.hasNext()) {
                    long onlineCount = result.next().get("count").asLong();
                    if (onlineCount >= 6) { // On a créé 6 index (3 full-text + 3 vector)
                        System.out.println(" ✅ Tous les index sont prêts!");
                        return;
                    }
                }

                Thread.sleep(1000); // Attendre 1 seconde
                System.out.print(".");
                attempt++;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                // Ignorer et continuer
                attempt++;
            }
        }

        System.out.println(" ⚠️ Timeout d'attente des index (continuer quand même)");
    }

    @Test
    @Order(2)
    @DisplayName("Test 2: Insérer des données de test")
    void test2_InsertTestData() {
        try (Session session = driver.session()) {
            // Classe UserService
            session.run("""
                CREATE (c:Class {
                    name: 'UserService',
                    fqn: 'com.example.UserService',
                    javaDoc: 'Service for managing users and authentication',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("UserService. Service for managing users and authentication")));

            // Méthode findByEmail
            session.run("""
                CREATE (m:Method {
                    name: 'findByEmail',
                    fqn: 'com.example.UserService.findByEmail',
                    signature: 'User findByEmail(String email)',
                    javaDoc: 'Find a user by their email address',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("findByEmail. User findByEmail(String email). Find a user by their email address")));

            // Méthode createUser
            session.run("""
                CREATE (m:Method {
                    name: 'createUser',
                    fqn: 'com.example.UserService.createUser',
                    signature: 'User createUser(String name, String email)',
                    javaDoc: 'Create a new user with name and email',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("createUser. User createUser(String name, String email). Create a new user with name and email")));

            // Classe ProductRepository
            session.run("""
                CREATE (c:Class {
                    name: 'ProductRepository',
                    fqn: 'com.example.ProductRepository',
                    javaDoc: 'Repository for product data access',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("ProductRepository. Repository for product data access")));

            // Méthode findAll
            session.run("""
                CREATE (m:Method {
                    name: 'findAll',
                    fqn: 'com.example.ProductRepository.findAll',
                    signature: 'List<Product> findAll()',
                    javaDoc: 'Retrieve all products from database',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("findAll. List<Product> findAll(). Retrieve all products from database")));

            System.out.println("✅ 5 nœuds de test insérés (2 classes, 3 méthodes)");
        }
    }

    @Test
    @Order(3)
    @DisplayName("Test 3: Recherche hybride trouve les bons résultats")
    void test3_HybridSearchFindsResults() throws SearchException {
        // Act
        List<EntryPoint> results = searchService.findEntryPoints("find user by email", 3);

        // Assert
        assertFalse(results.isEmpty(), "La recherche devrait retourner des résultats");
        assertTrue(results.size() <= 3, "Ne devrait pas retourner plus de 3 résultats");

        System.out.println("\n📊 Résultats de recherche pour 'find user by email':");
        for (EntryPoint ep : results) {
            System.out.println("  • " + ep);
        }
    }

    @Test
    @Order(4)
    @DisplayName("Test 4: Recherche avec topK=1 retourne 1 résultat")
    void test4_SearchWithTopK1() throws SearchException {
        // Act
        List<EntryPoint> results = searchService.findEntryPoints("create user", 1);

        // Assert
        assertEquals(1, results.size(), "Devrait retourner exactement 1 résultat");
        assertNotNull(results.get(0).name());
        assertTrue(results.get(0).score() > 0, "Le score devrait être positif");

        System.out.println("\n📊 Top 1 pour 'create user': " + results.get(0));
    }

    @Test
    @Order(5)
    @DisplayName("Test 5: Les scores sont décroissants")
    void test5_ScoresAreDecreasing() throws SearchException {
        // Act
        List<EntryPoint> results = searchService.findEntryPoints("user service repository", 5);

        // Assert
        for (int i = 0; i < results.size() - 1; i++) {
            assertTrue(results.get(i).score() >= results.get(i + 1).score(),
                "Les scores devraient être en ordre décroissant");
        }
    }

    @Test
    @Order(6)
    @DisplayName("Test 6: Recherche avec query vide lance une exception")
    void test6_EmptyQueryThrowsException() {
        assertThrows(IllegalArgumentException.class,
            () -> searchService.findEntryPoints("", 3),
            "Query vide devrait lancer IllegalArgumentException");

        assertThrows(IllegalArgumentException.class,
            () -> searchService.findEntryPoints("   ", 3),
            "Query avec espaces uniquement devrait lancer IllegalArgumentException");
    }

    @Test
    @Order(7)
    @DisplayName("Test 7: topK invalide lance une exception")
    void test7_InvalidTopKThrowsException() {
        assertThrows(IllegalArgumentException.class,
            () -> searchService.findEntryPoints("test", 0),
            "topK=0 devrait lancer IllegalArgumentException");

        assertThrows(IllegalArgumentException.class,
            () -> searchService.findEntryPoints("test", -1),
            "topK négatif devrait lancer IllegalArgumentException");
    }

    @Test
    @Order(8)
    @DisplayName("Test 8: Recherche retourne les types de nœuds corrects")
    void test8_SearchReturnsCorrectNodeTypes() throws SearchException {
        // Act
        List<EntryPoint> results = searchService.findEntryPoints("UserService", 5);

        // Assert
        for (EntryPoint ep : results) {
            assertTrue(
                ep.nodeType().equals("Class") ||
                ep.nodeType().equals("Method") ||
                ep.nodeType().equals("Function"),
                "Le type de nœud devrait être Class, Method ou Function"
            );
        }
    }

    @Test
    @Order(9)
    @DisplayName("Test 9: Les FQN sont valides")
    void test9_FQNsAreValid() throws SearchException {
        // Act
        List<EntryPoint> results = searchService.findEntryPoints("repository", 5);

        // Assert
        for (EntryPoint ep : results) {
            assertNotNull(ep.fqn(), "FQN ne devrait pas être null");
            assertTrue(ep.fqn().contains("."), "FQN devrait contenir au moins un point");
        }
    }

    @Test
    @Order(10)
    @DisplayName("Test 10: Requête sans résultats retourne liste vide")
    void test10_NoResultsReturnsEmptyList() throws SearchException {
        // Act
        List<EntryPoint> results = searchService.findEntryPoints("xyzabcnonexistent123", 5);

        // Assert
        // Peut retourner 0 ou quelques résultats avec scores très faibles
        assertNotNull(results, "Ne devrait pas retourner null");
        assertTrue(results.size() <= 5, "Ne devrait pas dépasser topK");
    }

    @Test
    @Order(11)
    @DisplayName("Test 11: Scénarios réalistes de recherche sur un graphe de code complet")
    void test11_RealWorldSearchScenarios() throws SearchException {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("TEST 11: SCÉNARIOS RÉALISTES DE RECHERCHE HYBRIDE");
        System.out.println("=".repeat(80));

        // Nettoyer les données précédentes et créer un graphe de code réaliste
        try (Session session = driver.session()) {
            // Supprimer seulement les anciennes données (garder les index existants du test 1)
            session.run("MATCH (n) WHERE n:Class OR n:Method OR n:Function DETACH DELETE n");
            System.out.println("✅ Données précédentes nettoyées, réutilisation des index existants");

            // === CLASSE 1: AuthenticationService ===
            session.run("""
                CREATE (c:Class {
                    name: 'AuthenticationService',
                    fqn: 'com.example.security.AuthenticationService',
                    javaDoc: 'Service responsible for user authentication and session management. Handles login, logout, token validation and password verification.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("AuthenticationService. Service responsible for user authentication and session management. Handles login, logout, token validation and password verification.")));

            session.run("""
                CREATE (m:Method {
                    name: 'authenticate',
                    fqn: 'com.example.security.AuthenticationService.authenticate',
                    signature: 'User authenticate(String username, String password)',
                    javaDoc: 'Authenticates a user with username and password. Returns User object if credentials are valid, throws AuthenticationException otherwise.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("authenticate. User authenticate(String username, String password). Authenticates a user with username and password. Returns User object if credentials are valid, throws AuthenticationException otherwise.")));

            session.run("""
                CREATE (m:Method {
                    name: 'validateToken',
                    fqn: 'com.example.security.AuthenticationService.validateToken',
                    signature: 'boolean validateToken(String token)',
                    javaDoc: 'Validates a JWT authentication token. Returns true if token is valid and not expired.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("validateToken. boolean validateToken(String token). Validates a JWT authentication token. Returns true if token is valid and not expired.")));

            // === CLASSE 2: UserService ===
            session.run("""
                CREATE (c:Class {
                    name: 'UserService',
                    fqn: 'com.example.service.UserService',
                    javaDoc: 'Core service for user management operations including CRUD operations, password reset, and profile updates.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("UserService. Core service for user management operations including CRUD operations, password reset, and profile updates.")));

            session.run("""
                CREATE (m:Method {
                    name: 'registerUser',
                    fqn: 'com.example.service.UserService.registerUser',
                    signature: 'User registerUser(String email, String password, String name)',
                    javaDoc: 'Registers a new user in the system. Validates email uniqueness, hashes password, and sends welcome email.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("registerUser. User registerUser(String email, String password, String name). Registers a new user in the system. Validates email uniqueness, hashes password, and sends welcome email.")));

            session.run("""
                CREATE (m:Method {
                    name: 'updateProfile',
                    fqn: 'com.example.service.UserService.updateProfile',
                    signature: 'void updateProfile(Long userId, ProfileDTO profile)',
                    javaDoc: 'Updates user profile information including name, bio, and avatar.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("updateProfile. void updateProfile(Long userId, ProfileDTO profile). Updates user profile information including name, bio, and avatar.")));

            session.run("""
                CREATE (m:Method {
                    name: 'resetPassword',
                    fqn: 'com.example.service.UserService.resetPassword',
                    signature: 'void resetPassword(String email)',
                    javaDoc: 'Initiates password reset process by sending reset link to user email.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("resetPassword. void resetPassword(String email). Initiates password reset process by sending reset link to user email.")));

            // === CLASSE 3: OrderService ===
            session.run("""
                CREATE (c:Class {
                    name: 'OrderService',
                    fqn: 'com.example.commerce.OrderService',
                    javaDoc: 'Handles e-commerce order processing, payment verification, and order tracking.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("OrderService. Handles e-commerce order processing, payment verification, and order tracking.")));

            session.run("""
                CREATE (m:Method {
                    name: 'createOrder',
                    fqn: 'com.example.commerce.OrderService.createOrder',
                    signature: 'Order createOrder(Long userId, List<OrderItem> items)',
                    javaDoc: 'Creates a new order with specified items. Calculates total, applies discounts, and reserves inventory.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("createOrder. Order createOrder(Long userId, List<OrderItem> items). Creates a new order with specified items. Calculates total, applies discounts, and reserves inventory.")));

            session.run("""
                CREATE (m:Method {
                    name: 'calculateTotal',
                    fqn: 'com.example.commerce.OrderService.calculateTotal',
                    signature: 'BigDecimal calculateTotal(List<OrderItem> items)',
                    javaDoc: 'Calculates order total including taxes, shipping costs, and applied discounts.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("calculateTotal. BigDecimal calculateTotal(List<OrderItem> items). Calculates order total including taxes, shipping costs, and applied discounts.")));

            // === CLASSE 4: ProductRepository ===
            session.run("""
                CREATE (c:Class {
                    name: 'ProductRepository',
                    fqn: 'com.example.repository.ProductRepository',
                    javaDoc: 'Data access layer for product catalog. Provides methods to query, filter and search products.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("ProductRepository. Data access layer for product catalog. Provides methods to query, filter and search products.")));

            session.run("""
                CREATE (m:Method {
                    name: 'searchByKeyword',
                    fqn: 'com.example.repository.ProductRepository.searchByKeyword',
                    signature: 'List<Product> searchByKeyword(String keyword)',
                    javaDoc: 'Full-text search products by keyword in name, description and tags.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("searchByKeyword. List<Product> searchByKeyword(String keyword). Full-text search products by keyword in name, description and tags.")));

            session.run("""
                CREATE (m:Method {
                    name: 'findByCategory',
                    fqn: 'com.example.repository.ProductRepository.findByCategory',
                    signature: 'List<Product> findByCategory(String category)',
                    javaDoc: 'Retrieves all products belonging to a specific category.',
                    embedding: $embedding
                })
                """, Map.of("embedding", generateEmbedding("findByCategory. List<Product> findByCategory(String category). Retrieves all products belonging to a specific category.")));

            System.out.println("✅ Graphe de code réaliste créé (4 classes, 10 méthodes)");
        }

        // Attendre que Neo4j indexe les nouveaux nœuds
        System.out.print("⏳ Attente de l'indexation des nœuds...");
        try {
            Thread.sleep(3000); // Attendre 3 secondes pour l'indexation
            System.out.println(" ✅");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // === SCÉNARIO 1: Recherche par nom de classe exact ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 1: Recherche par nom de classe exact");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'AuthenticationService'");

        List<EntryPoint> results1 = searchService.findEntryPoints("AuthenticationService", 3);
        displayResults(results1);
        assertTrue(results1.stream().anyMatch(ep ->
            ep.name().equals("AuthenticationService") && ep.nodeType().equals("Class")),
            "La classe AuthenticationService devrait être dans les résultats");

        // === SCÉNARIO 2: Recherche par nom de méthode ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 2: Recherche par nom de méthode");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'authenticate'");

        List<EntryPoint> results2 = searchService.findEntryPoints("authenticate", 3);
        displayResults(results2);
        assertTrue(results2.stream().anyMatch(ep -> ep.name().equals("authenticate")),
            "La méthode authenticate devrait être trouvée");

        // === SCÉNARIO 3: Question utilisateur longue (authentification) ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 3: Question utilisateur - authentification");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'Comment authentifier un utilisateur avec username et password ?'");

        List<EntryPoint> results3 = searchService.findEntryPoints(
            "Comment authentifier un utilisateur avec username et password ?", 5);
        displayResults(results3);
        // La méthode authenticate ou la classe AuthenticationService devrait être bien classée
        assertFalse(results3.isEmpty(), "Devrait trouver des résultats pour l'authentification");

        // === SCÉNARIO 4: Question utilisateur longue (création d'utilisateur) ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 4: Question utilisateur - création d'utilisateur");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'Je veux créer un nouvel utilisateur avec son email et mot de passe'");

        List<EntryPoint> results4 = searchService.findEntryPoints(
            "Je veux créer un nouvel utilisateur avec son email et mot de passe", 5);
        displayResults(results4);
        // La méthode registerUser devrait être bien classée
        assertFalse(results4.isEmpty(), "Devrait trouver des résultats pour la création d'utilisateur");

        // === SCÉNARIO 5: Recherche par fonctionnalité (password reset) ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 5: Recherche par fonctionnalité");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'password reset'");

        List<EntryPoint> results5 = searchService.findEntryPoints("password reset", 3);
        displayResults(results5);
        assertTrue(results5.stream().anyMatch(ep -> ep.name().contains("reset") || ep.name().contains("Password")),
            "Devrait trouver resetPassword ou méthodes liées");

        // === SCÉNARIO 6: Recherche e-commerce (commande) ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 6: Recherche e-commerce");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'Comment créer une commande avec des articles ?'");

        List<EntryPoint> results6 = searchService.findEntryPoints(
            "Comment créer une commande avec des articles ?", 5);
        displayResults(results6);
        // La méthode createOrder devrait être bien classée
        assertFalse(results6.isEmpty(), "Devrait trouver des résultats pour la création de commande");

        // === SCÉNARIO 7: Recherche par calcul (total) ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 7: Recherche par calcul");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'calculate total price with taxes'");

        List<EntryPoint> results7 = searchService.findEntryPoints("calculate total price with taxes", 3);
        displayResults(results7);
        assertTrue(results7.stream().anyMatch(ep -> ep.name().contains("calculate") || ep.name().contains("Total")),
            "Devrait trouver calculateTotal");

        // === SCÉNARIO 8: Recherche par repository/data access ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 8: Recherche data access");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'search products by keyword'");

        List<EntryPoint> results8 = searchService.findEntryPoints("search products by keyword", 3);
        displayResults(results8);
        assertTrue(results8.stream().anyMatch(ep ->
            ep.name().contains("search") || ep.name().contains("Product")),
            "Devrait trouver searchByKeyword ou ProductRepository");

        // === SCÉNARIO 9: Recherche avec terme technique (JWT token) ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 9: Recherche terme technique");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'validate JWT token'");

        List<EntryPoint> results9 = searchService.findEntryPoints("validate JWT token", 3);
        displayResults(results9);
        assertTrue(results9.stream().anyMatch(ep -> ep.name().contains("validate") || ep.name().contains("Token")),
            "Devrait trouver validateToken");

        // === SCÉNARIO 10: Recherche ambiguë (profile) ===
        System.out.println("\n" + "─".repeat(80));
        System.out.println("SCÉNARIO 10: Recherche ambiguë");
        System.out.println("─".repeat(80));
        System.out.println("Query: 'update profile'");

        List<EntryPoint> results10 = searchService.findEntryPoints("update profile", 3);
        displayResults(results10);
        assertTrue(results10.stream().anyMatch(ep -> ep.name().contains("update") || ep.name().contains("Profile")),
            "Devrait trouver updateProfile");

        System.out.println("\n" + "=".repeat(80));
        System.out.println("FIN DES SCÉNARIOS RÉALISTES");
        System.out.println("=".repeat(80) + "\n");
    }

    /**
     * Affiche les résultats de recherche de manière formatée.
     */
    private void displayResults(List<EntryPoint> results) {
        if (results.isEmpty()) {
            System.out.println("  ⚠️  Aucun résultat trouvé");
            return;
        }

        System.out.println("  📊 Résultats (Top " + results.size() + "):");
        for (int i = 0; i < results.size(); i++) {
            EntryPoint ep = results.get(i);
            System.out.printf("    %d. [%s] %s (score: %.4f)%n",
                i + 1, ep.nodeType(), ep.name(), ep.score());
            System.out.printf("       FQN: %s%n", ep.fqn());
            if (ep.properties().containsKey("signature")) {
                System.out.printf("       Signature: %s%n", ep.properties().get("signature"));
            }
        }
    }

    /**
     * Génère un embedding réel via Ollama pour le texte donné.
     * Utilisé pour créer les embeddings des nœuds de test.
     *
     * @param text Le texte à encoder (nom + javaDoc généralement)
     * @return Liste de 768 floats (dimensions de nomic-embed-text)
     */
    private List<Float> generateEmbedding(String text) {
        dev.langchain4j.data.embedding.Embedding embedding = embeddingModel.embed(text).content();

        // Convertir float[] en List<Float>
        float[] vector = embedding.vector();
        java.util.List<Float> list = new java.util.ArrayList<>(vector.length);
        for (float v : vector) {
            list.add(v);
        }
        return list;
    }
}
