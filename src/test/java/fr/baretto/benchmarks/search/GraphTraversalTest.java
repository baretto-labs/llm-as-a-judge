package fr.baretto.benchmarks.search;

import org.junit.jupiter.api.*;
import org.neo4j.driver.*;
import org.testcontainers.containers.Neo4jContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests pour GraphTraversal (expansion K-hop, path finding, subgraph extraction).
 * Utilise Testcontainers pour avoir un vrai Neo4j.
 */
@Testcontainers
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class GraphTraversalTest {

    @Container
    private static final Neo4jContainer<?> neo4jContainer = new Neo4jContainer<>("neo4j:5.15")
        .withAdminPassword("test1234");

    private static Driver driver;
    private static GraphTraversal graphTraversal;

    // IDs des nœuds de test (seront assignés après création)
    private static long authServiceId;
    private static long authenticateMethodId;
    private static long userRepositoryId;
    private static long findByUsernameId;
    private static long userClassId;

    @BeforeAll
    static void setup() {
        driver = GraphDatabase.driver(
            neo4jContainer.getBoltUrl(),
            AuthTokens.basic("neo4j", "test1234")
        );

        graphTraversal = new GraphTraversal(driver);

        // Créer un graphe de test
        createTestGraph();
    }

    @AfterAll
    static void tearDown() {
        if (driver != null) {
            driver.close();
        }
    }

    /**
     * Crée un graphe de test représentant une chaîne d'appels typique:
     * AuthenticationService.authenticate() → UserRepository.findByUsername() → User
     */
    private static void createTestGraph() {
        try (Session session = driver.session()) {
            // Classe AuthenticationService
            var result1 = session.run("""
                CREATE (c:Class {
                    name: 'AuthenticationService',
                    fqn: 'com.example.AuthenticationService',
                    javaDoc: 'Service for user authentication'
                })
                RETURN id(c) as nodeId
                """);
            authServiceId = result1.single().get("nodeId").asLong();

            // Méthode authenticate
            var result2 = session.run("""
                CREATE (m:Method {
                    name: 'authenticate',
                    fqn: 'com.example.AuthenticationService.authenticate',
                    signature: 'User authenticate(String username, String password)',
                    javaDoc: 'Authenticates a user'
                })
                RETURN id(m) as nodeId
                """);
            authenticateMethodId = result2.single().get("nodeId").asLong();

            // Classe UserRepository
            var result3 = session.run("""
                CREATE (c:Class {
                    name: 'UserRepository',
                    fqn: 'com.example.UserRepository',
                    javaDoc: 'Repository for user data'
                })
                RETURN id(c) as nodeId
                """);
            userRepositoryId = result3.single().get("nodeId").asLong();

            // Méthode findByUsername
            var result4 = session.run("""
                CREATE (m:Method {
                    name: 'findByUsername',
                    fqn: 'com.example.UserRepository.findByUsername',
                    signature: 'User findByUsername(String username)',
                    javaDoc: 'Finds user by username'
                })
                RETURN id(m) as nodeId
                """);
            findByUsernameId = result4.single().get("nodeId").asLong();

            // Classe User
            var result5 = session.run("""
                CREATE (c:Class {
                    name: 'User',
                    fqn: 'com.example.User',
                    javaDoc: 'User entity'
                })
                RETURN id(c) as nodeId
                """);
            userClassId = result5.single().get("nodeId").asLong();

            // Créer les relations
            session.run("""
                MATCH (authService), (authMethod)
                WHERE id(authService) = $authServiceId AND id(authMethod) = $authenticateId
                CREATE (authService)-[:DECLARES]->(authMethod)
                """, Map.of("authServiceId", authServiceId, "authenticateId", authenticateMethodId));

            session.run("""
                MATCH (authMethod), (findMethod)
                WHERE id(authMethod) = $authenticateId AND id(findMethod) = $findId
                CREATE (authMethod)-[:CALLS]->(findMethod)
                """, Map.of("authenticateId", authenticateMethodId, "findId", findByUsernameId));

            session.run("""
                MATCH (userRepo), (findMethod)
                WHERE id(userRepo) = $repoId AND id(findMethod) = $findId
                CREATE (userRepo)-[:DECLARES]->(findMethod)
                """, Map.of("repoId", userRepositoryId, "findId", findByUsernameId));

            session.run("""
                MATCH (findMethod), (userClass)
                WHERE id(findMethod) = $findId AND id(userClass) = $userId
                CREATE (findMethod)-[:RETURNS]->(userClass)
                """, Map.of("findId", findByUsernameId, "userId", userClassId));

            session.run("""
                MATCH (authMethod), (userClass)
                WHERE id(authMethod) = $authenticateId AND id(userClass) = $userId
                CREATE (authMethod)-[:RETURNS]->(userClass)
                """, Map.of("authenticateId", authenticateMethodId, "userId", userClassId));

            System.out.println("✅ Graphe de test créé:");
            System.out.println("   AuthenticationService (id=" + authServiceId + ")");
            System.out.println("   └─ DECLARES → authenticate() (id=" + authenticateMethodId + ")");
            System.out.println("       └─ CALLS → findByUsername() (id=" + findByUsernameId + ")");
            System.out.println("           └─ RETURNS → User (id=" + userClassId + ")");
        }
    }

    @Test
    @Order(1)
    @DisplayName("Test 1: K-hop expansion 1 saut")
    void test1_KHopExpansion1Hop() throws SearchException {
        // Partir de authenticate(), trouver voisins à 1 saut
        Map<Long, Integer> expansion = graphTraversal.expandKHop(
            List.of(authenticateMethodId),
            1,
            null // Toutes relations
        );

        // Devrait trouver: AuthenticationService (DECLARES), findByUsername (CALLS), User (RETURNS)
        assertTrue(expansion.size() >= 3, "Devrait trouver au moins 3 voisins à 1 saut");
        assertTrue(expansion.containsKey(authServiceId), "Devrait trouver AuthenticationService");
        assertTrue(expansion.containsKey(findByUsernameId), "Devrait trouver findByUsername");
        assertTrue(expansion.containsKey(userClassId), "Devrait trouver User");

        // Vérifier distances
        assertEquals(1, expansion.get(authServiceId), "AuthenticationService devrait être à distance 1");
        assertEquals(1, expansion.get(findByUsernameId), "findByUsername devrait être à distance 1");
    }

    @Test
    @Order(2)
    @DisplayName("Test 2: K-hop expansion 2 sauts")
    void test2_KHopExpansion2Hops() throws SearchException {
        // Partir de authenticate(), trouver voisins à 2 sauts
        Map<Long, Integer> expansion = graphTraversal.expandKHop(
            List.of(authenticateMethodId),
            2,
            null
        );

        // Devrait trouver UserRepository à distance 2 (via findByUsername)
        assertTrue(expansion.size() >= 4, "Devrait trouver au moins 4 nœuds à 2 sauts");
        assertTrue(expansion.containsKey(userRepositoryId), "Devrait trouver UserRepository");

        // Vérifier distance
        assertEquals(2, expansion.get(userRepositoryId), "UserRepository devrait être à distance 2");
    }

    @Test
    @Order(3)
    @DisplayName("Test 3: K-hop avec filtre de relations CALLS uniquement")
    void test3_KHopWithRelationFilter() throws SearchException {
        // Partir de authenticate(), suivre uniquement CALLS
        Map<Long, Integer> expansion = graphTraversal.expandKHop(
            List.of(authenticateMethodId),
            2,
            List.of("CALLS")
        );

        // Devrait trouver findByUsername (CALLS direct)
        assertTrue(expansion.containsKey(findByUsernameId), "Devrait trouver findByUsername via CALLS");

        // Ne devrait PAS trouver AuthenticationService (relation DECLARES, pas CALLS)
        assertFalse(expansion.containsKey(authServiceId),
            "Ne devrait PAS trouver AuthenticationService (filtre CALLS uniquement)");
    }

    @Test
    @Order(4)
    @DisplayName("Test 4: Trouver chemins entre 2 nœuds")
    void test4_FindPathsBetweenNodes() throws SearchException {
        // Trouver chemins entre authenticate() et User
        List<GraphTraversal.GraphPath> paths = graphTraversal.findPaths(
            List.of(authenticateMethodId),
            List.of(userClassId),
            4
        );

        assertFalse(paths.isEmpty(), "Devrait trouver au moins un chemin");

        // Premier chemin devrait être le plus court
        GraphTraversal.GraphPath shortestPath = paths.get(0);
        assertNotNull(shortestPath, "Le chemin ne devrait pas être null");
        assertEquals(authenticateMethodId, shortestPath.sourceId(), "Source devrait être authenticate()");
        assertEquals(userClassId, shortestPath.targetId(), "Target devrait être User");

        // Vérifier que le chemin contient bien les nœuds intermédiaires
        assertTrue(shortestPath.nodeIds().size() >= 2, "Le chemin devrait contenir au moins 2 nœuds");

        // Vérifier le type de relations
        assertFalse(shortestPath.relationTypes().isEmpty(), "Le chemin devrait avoir des relations");

        System.out.println("Chemin trouvé: " + shortestPath.nodeIds().size() + " nœuds, " +
            shortestPath.length() + " sauts, score=" + shortestPath.score());
    }

    @Test
    @Order(5)
    @DisplayName("Test 5: Path ranking - chemin court meilleur score")
    void test5_PathRanking() throws SearchException {
        // Trouver tous les chemins
        List<GraphTraversal.GraphPath> paths = graphTraversal.findPaths(
            List.of(authenticateMethodId),
            List.of(userClassId),
            4
        );

        if (paths.size() > 1) {
            // Les chemins devraient être triés par score décroissant
            for (int i = 0; i < paths.size() - 1; i++) {
                double score1 = paths.get(i).score();
                double score2 = paths.get(i + 1).score();
                assertTrue(score1 >= score2,
                    "Les chemins devraient être triés par score décroissant");
            }
        }
    }

    @Test
    @Order(6)
    @DisplayName("Test 6: Extraction de sous-graphe radius=1")
    void test6_SubgraphExtraction1() throws SearchException {
        // Extraire sous-graphe autour de authenticate()
        GraphTraversal.Subgraph subgraph = graphTraversal.extractSubgraph(
            List.of(authenticateMethodId),
            1
        );

        assertFalse(subgraph.nodes().isEmpty(), "Le sous-graphe ne devrait pas être vide");

        // Vérifier que le nœud central a le meilleur score (distance 0)
        List<GraphTraversal.SubgraphNode> sortedNodes = subgraph.sortedByScore();
        GraphTraversal.SubgraphNode topNode = sortedNodes.get(0);

        // Le top node devrait être à distance 0 ou 1
        assertTrue(topNode.distance() <= 1, "Le nœud avec meilleur score devrait être proche");
        assertTrue(topNode.score() > 0, "Le score devrait être positif");

        System.out.println("Sous-graphe extrait: " + subgraph.nodes().size() + " nœuds");
        System.out.println("Top node: " + topNode.name() + " (distance=" + topNode.distance() +
            ", score=" + topNode.score() + ")");
    }

    @Test
    @Order(7)
    @DisplayName("Test 7: Extraction de sous-graphe radius=2")
    void test7_SubgraphExtraction2() throws SearchException {
        // Extraire sous-graphe autour de authenticate() avec radius=2
        GraphTraversal.Subgraph subgraph = graphTraversal.extractSubgraph(
            List.of(authenticateMethodId),
            2
        );

        // Devrait trouver plus de nœuds qu'avec radius=1
        assertTrue(subgraph.nodes().size() >= 3, "Devrait trouver au moins 3 nœuds avec radius=2");

        // Vérifier que UserRepository est inclus (distance 2)
        boolean foundUserRepo = subgraph.nodes().stream()
            .anyMatch(node -> node.nodeId() == userRepositoryId);
        assertTrue(foundUserRepo, "Devrait trouver UserRepository à distance 2");
    }

    @Test
    @Order(8)
    @DisplayName("Test 8: Filtre sous-graphe par distance")
    void test8_SubgraphFilterByDistance() throws SearchException {
        // Extraire sous-graphe radius=2
        GraphTraversal.Subgraph subgraph = graphTraversal.extractSubgraph(
            List.of(authenticateMethodId),
            2
        );

        // Filtrer pour ne garder que distance <= 1
        List<GraphTraversal.SubgraphNode> closeNodes = subgraph.filterByDistance(1);

        // Tous les nœuds devraient avoir distance <= 1
        for (GraphTraversal.SubgraphNode node : closeNodes) {
            assertTrue(node.distance() <= 1,
                "Nœud " + node.name() + " devrait avoir distance <= 1");
        }

        // Devrait y avoir moins de nœuds que le graphe complet
        assertTrue(closeNodes.size() <= subgraph.nodes().size(),
            "Le filtre devrait réduire le nombre de nœuds");
    }

    @Test
    @Order(9)
    @DisplayName("Test 9: Expansion depuis liste vide retourne map vide")
    void test9_EmptyInputReturnsEmpty() throws SearchException {
        Map<Long, Integer> expansion = graphTraversal.expandKHop(
            List.of(),
            1,
            null
        );

        assertTrue(expansion.isEmpty(), "Expansion depuis liste vide devrait retourner map vide");
    }

    @Test
    @Order(10)
    @DisplayName("Test 10: Validation paramètres invalides")
    void test10_ValidationInvalidParams() {
        // maxHops invalide
        assertThrows(IllegalArgumentException.class, () ->
            graphTraversal.expandKHop(List.of(authenticateMethodId), 0, null),
            "maxHops=0 devrait lancer exception");

        assertThrows(IllegalArgumentException.class, () ->
            graphTraversal.expandKHop(List.of(authenticateMethodId), 10, null),
            "maxHops=10 devrait lancer exception");

        // maxPathLength invalide
        assertThrows(IllegalArgumentException.class, () ->
            graphTraversal.findPaths(List.of(authenticateMethodId), List.of(userClassId), 0),
            "maxPathLength=0 devrait lancer exception");

        // radius invalide
        assertThrows(IllegalArgumentException.class, () ->
            graphTraversal.extractSubgraph(List.of(authenticateMethodId), 0),
            "radius=0 devrait lancer exception");

        assertThrows(IllegalArgumentException.class, () ->
            graphTraversal.extractSubgraph(List.of(authenticateMethodId), 5),
            "radius=5 devrait lancer exception");
    }

    @Test
    @Order(11)
    @DisplayName("Test 11: Score décroissant avec distance croissante")
    void test11_ScoreDecreasesWithDistance() throws SearchException {
        GraphTraversal.Subgraph subgraph = graphTraversal.extractSubgraph(
            List.of(authenticateMethodId),
            2
        );

        // Trouver nœuds à distance 0, 1, 2
        Map<Integer, Double> avgScoreByDistance = subgraph.nodes().stream()
            .collect(java.util.stream.Collectors.groupingBy(
                GraphTraversal.SubgraphNode::distance,
                java.util.stream.Collectors.averagingDouble(GraphTraversal.SubgraphNode::score)
            ));

        // Score moyen devrait décroître avec la distance
        if (avgScoreByDistance.containsKey(0) && avgScoreByDistance.containsKey(1)) {
            assertTrue(avgScoreByDistance.get(0) >= avgScoreByDistance.get(1),
                "Score moyen à distance 0 devrait être >= score à distance 1");
        }

        if (avgScoreByDistance.containsKey(1) && avgScoreByDistance.containsKey(2)) {
            assertTrue(avgScoreByDistance.get(1) >= avgScoreByDistance.get(2),
                "Score moyen à distance 1 devrait être >= score à distance 2");
        }
    }

    @Test
    @Order(12)
    @DisplayName("Test 12: Multiple nœuds centraux pour subgraph")
    void test12_MultipleNodesForSubgraph() throws SearchException {
        // Extraire sous-graphe autour de 2 nœuds centraux
        GraphTraversal.Subgraph subgraph = graphTraversal.extractSubgraph(
            List.of(authenticateMethodId, findByUsernameId),
            1
        );

        assertFalse(subgraph.nodes().isEmpty(), "Le sous-graphe ne devrait pas être vide");

        // Devrait inclure les deux nœuds centraux et leurs voisins
        assertTrue(subgraph.nodes().size() >= 2,
            "Devrait avoir au moins les 2 nœuds centraux");
    }
}
