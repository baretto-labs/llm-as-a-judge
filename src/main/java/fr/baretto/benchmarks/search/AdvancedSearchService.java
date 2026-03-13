package fr.baretto.benchmarks.search;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import org.neo4j.driver.Driver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Service de recherche avancé intégrant toutes les fonctionnalités GraphRAG state-of-the-art 2026 :
 * <ol>
 *   <li><b>Hybrid Search</b> : BM25 + Vector + RRF (HybridSearchService)</li>
 *   <li><b>Graph Traversal</b> : K-hop expansion pour contexte élargi (GraphTraversal)</li>
 *   <li><b>Community Detection</b> : Recherche globale dans clusters (CommunityDetection)</li>
 *   <li><b>LLM Reranking</b> : Affinement sémantique des résultats (LLMReranker)</li>
 * </ol>
 *
 * <p><b>Architecture Pipeline</b> :</p>
 * <pre>
 * Query → [1. Hybrid Search] → Top 10 RRF
 *      ↓  [2. Graph Expansion] → +K-hop neighbors (contexte)
 *      ↓  [3. LLM Reranking]   → Top K rerankés
 *      → EntryPoints enrichis
 * </pre>
 *
 * <p><b>Mode Global Search</b> (via communities) :</p>
 * <pre>
 * Query → [1. Detect Communities] → Clusters fonctionnels
 *      ↓  [2. Search in Communities] → Top K communities
 *      ↓  [3. Expand with Graph] → Classes + méthodes du cluster
 *      → EntryPoints du module
 * </pre>
 */
public class AdvancedSearchService implements GraphSearchHook {

    private static final Logger logger = LoggerFactory.getLogger(AdvancedSearchService.class);

    private final HybridSearchService hybridSearch;
    private final GraphTraversal graphTraversal;
    private final LLMReranker llmReranker;
    private final CommunityDetection communityDetection;

    private final boolean enableGraphExpansion;
    private final boolean enableLLMReranking;
    private final int graphExpansionHops;

    /**
     * Constructeur complet avec toutes les fonctionnalités.
     *
     * @param neo4jDriver         Driver Neo4j
     * @param embeddingModel      Modèle d'embedding pour recherche vectorielle
     * @param llmModel            Modèle LLM pour reranking et résumés (peut être null)
     * @param enableGraphExpansion Active l'expansion K-hop (recommandé: true)
     * @param enableLLMReranking  Active le reranking LLM (nécessite llmModel non-null)
     * @param graphExpansionHops  Nombre de sauts pour expansion (recommandé: 1-2)
     */
    public AdvancedSearchService(
        Driver neo4jDriver,
        EmbeddingModel embeddingModel,
        ChatModel llmModel,
        boolean enableGraphExpansion,
        boolean enableLLMReranking,
        int graphExpansionHops
    ) {
        Objects.requireNonNull(neo4jDriver, "neo4jDriver ne peut pas être null");
        Objects.requireNonNull(embeddingModel, "embeddingModel ne peut pas être null");

        this.hybridSearch = new HybridSearchService(neo4jDriver, embeddingModel);
        this.graphTraversal = new GraphTraversal(neo4jDriver);
        this.llmReranker = llmModel != null ? new LLMReranker(llmModel) : null;
        this.communityDetection = new CommunityDetection(neo4jDriver, llmModel);

        this.enableGraphExpansion = enableGraphExpansion;
        this.enableLLMReranking = enableLLMReranking && llmModel != null;
        this.graphExpansionHops = Math.max(1, Math.min(graphExpansionHops, 3));

        logger.info("AdvancedSearchService initialisé (graphExpansion={}, llmReranking={}, hops={})",
            enableGraphExpansion, this.enableLLMReranking, this.graphExpansionHops);
    }

    /**
     * Constructeur simplifié avec configuration par défaut.
     * Graph expansion activée (1 hop), LLM reranking activé si LLM fourni.
     */
    public AdvancedSearchService(
        Driver neo4jDriver,
        EmbeddingModel embeddingModel,
        ChatModel llmModel
    ) {
        this(neo4jDriver, embeddingModel, llmModel, true, true, 1);
    }

    /**
     * Constructeur sans LLM (pas de reranking ni résumés).
     */
    public AdvancedSearchService(Driver neo4jDriver, EmbeddingModel embeddingModel) {
        this(neo4jDriver, embeddingModel, null, true, false, 1);
    }

    @Override
    public List<EntryPoint> findEntryPoints(String query, int topK) throws SearchException {
        Objects.requireNonNull(query, "query ne peut pas être null");
        if (query.isBlank()) {
            throw new IllegalArgumentException("query ne peut pas être vide");
        }
        if (topK <= 0) {
            throw new IllegalArgumentException("topK doit être > 0");
        }

        logger.info("Recherche avancée: query='{}', topK={}", query, topK);

        // ÉTAPE 1: Recherche hybride (BM25 + Vector + RRF)
        logger.debug("Étape 1/3: Hybrid Search");
        int intermediateTopK = Math.max(topK, 10); // Au moins 10 pour expansion
        List<EntryPoint> hybridResults = hybridSearch.findEntryPoints(query, intermediateTopK);

        if (hybridResults.isEmpty()) {
            logger.warn("Aucun résultat hybrid search pour: {}", query);
            return List.of();
        }

        logger.debug("Hybrid search: {} résultats", hybridResults.size());

        // ÉTAPE 2: Expansion graphe (optionnel)
        List<EntryPoint> expandedResults = hybridResults;
        if (enableGraphExpansion) {
            logger.debug("Étape 2/3: Graph Expansion ({} hops)", graphExpansionHops);
            expandedResults = expandWithGraph(hybridResults, graphExpansionHops);
            logger.debug("Après expansion: {} résultats", expandedResults.size());
        } else {
            logger.debug("Étape 2/3: Graph Expansion désactivée");
        }

        // ÉTAPE 3: Reranking LLM (optionnel)
        List<EntryPoint> finalResults = expandedResults;
        if (enableLLMReranking && llmReranker != null) {
            logger.debug("Étape 3/3: LLM Reranking");
            finalResults = llmReranker.rerank(query, expandedResults, topK);
            logger.debug("Après reranking: {} résultats", finalResults.size());
        } else {
            logger.debug("Étape 3/3: LLM Reranking désactivé");
            // Juste limiter au topK
            finalResults = expandedResults.stream().limit(topK).collect(Collectors.toList());
        }

        logger.info("Recherche avancée terminée: {} résultats", finalResults.size());
        return finalResults;
    }

    /**
     * Recherche globale basée sur les communautés (clusters fonctionnels).
     * <p>
     * Utilise la détection de communautés pour trouver des modules entiers correspondant à la requête.
     * Utile pour questions high-level comme "module d'authentification" ou "gestion des paiements".
     *
     * @param query                Requête utilisateur (ex: "authentication module")
     * @param topKCommunities      Nombre de communautés à retourner
     * @param minCommunitySize     Taille minimale d'une communauté (défaut: 3)
     * @param maxIterations        Itérations pour détection (défaut: 15)
     * @return Liste de communautés avec leurs nœuds
     * @throws SearchException Si erreur Neo4j
     */
    public List<CommunityDetection.Community> findCommunities(
        String query,
        int topKCommunities,
        int minCommunitySize,
        int maxIterations
    ) throws SearchException {
        Objects.requireNonNull(query, "query ne peut pas être null");
        if (query.isBlank()) {
            throw new IllegalArgumentException("query ne peut pas être vide");
        }

        logger.info("Recherche globale (communities): query='{}', topK={}", query, topKCommunities);

        // Détecter les communautés
        logger.debug("Détection de communautés (minSize={}, maxIter={})", minCommunitySize, maxIterations);
        List<CommunityDetection.Community> allCommunities = communityDetection.detectCommunities(
            minCommunitySize,
            maxIterations
        );

        logger.debug("Communautés détectées: {}", allCommunities.size());

        // Rechercher dans les communautés
        List<CommunityDetection.Community> matchedCommunities = communityDetection.searchCommunities(
            allCommunities,
            query,
            topKCommunities
        );

        logger.info("Recherche communautés terminée: {} communautés matchées", matchedCommunities.size());
        return matchedCommunities;
    }

    /**
     * Variante simplifiée avec paramètres par défaut.
     */
    public List<CommunityDetection.Community> findCommunities(String query, int topKCommunities) throws SearchException {
        return findCommunities(query, topKCommunities, 3, 15);
    }

    /**
     * Convertit les nœuds d'une communauté en EntryPoints.
     * Utile pour afficher les résultats d'une recherche globale.
     *
     * @param community Communauté à convertir
     * @param topK      Nombre de nœuds à retourner (classes en priorité)
     * @return Liste d'EntryPoints
     */
    public List<EntryPoint> communityToEntryPoints(CommunityDetection.Community community, int topK) {
        List<EntryPoint> entryPoints = new ArrayList<>();

        // Priorité aux classes
        for (CommunityDetection.CommunityNode node : community.getClasses()) {
            if (entryPoints.size() >= topK) break;

            Map<String, Object> properties = new HashMap<>();
            if (!node.javaDoc().isEmpty()) {
                properties.put("javaDoc", node.javaDoc());
            }

            entryPoints.add(new EntryPoint(
                node.nodeId(),
                node.nodeType(),
                node.name(),
                node.fqn(),
                1.0, // Score fixe pour community
                properties
            ));
        }

        // Compléter avec les méthodes
        for (CommunityDetection.CommunityNode node : community.getMethods()) {
            if (entryPoints.size() >= topK) break;

            Map<String, Object> properties = new HashMap<>();
            if (!node.javaDoc().isEmpty()) {
                properties.put("javaDoc", node.javaDoc());
            }

            entryPoints.add(new EntryPoint(
                node.nodeId(),
                node.nodeType(),
                node.name(),
                node.fqn(),
                0.8, // Score légèrement inférieur pour méthodes
                properties
            ));
        }

        return entryPoints;
    }

    /**
     * Expande les résultats avec le graphe K-hop.
     * Ajoute les voisins proches pour enrichir le contexte.
     */
    private List<EntryPoint> expandWithGraph(List<EntryPoint> initialResults, int hops) throws SearchException {
        if (initialResults.isEmpty()) {
            return initialResults;
        }

        // Extraire les IDs des résultats initiaux
        List<Long> initialIds = initialResults.stream()
            .map(EntryPoint::nodeId)
            .collect(Collectors.toList());

        // Expansion K-hop
        Map<Long, Integer> expansion = graphTraversal.expandKHop(initialIds, hops, null);

        logger.debug("Expansion K-hop: {} nœuds initiaux → {} nœuds total", initialIds.size(), expansion.size());

        // Récupérer les détails des nouveaux nœuds
        List<Long> newNodeIds = expansion.keySet().stream()
            .filter(id -> !initialIds.contains(id)) // Exclure les nœuds déjà présents
            .collect(Collectors.toList());

        if (newNodeIds.isEmpty()) {
            return initialResults;
        }

        List<EntryPoint> newNodes = fetchEntryPointsFromIds(newNodeIds, expansion);

        // Les résultats initiaux (pertinents pour la requête) restent en tête dans leur ordre RRF.
        // Les nœuds étendus (contexte supplémentaire) sont ajoutés après, triés par distance.
        List<EntryPoint> combined = new ArrayList<>(initialResults);
        newNodes.sort(Comparator.comparingDouble(EntryPoint::score).reversed());
        combined.addAll(newNodes);

        return combined;
    }

    /**
     * Récupère les EntryPoints depuis une liste d'IDs avec scores basés sur distance.
     */
    private List<EntryPoint> fetchEntryPointsFromIds(
        List<Long> nodeIds,
        Map<Long, Integer> distanceMap
    ) throws SearchException {
        if (nodeIds.isEmpty()) {
            return List.of();
        }

        return graphTraversal.fetchNodes(nodeIds, distanceMap).stream()
            .map(node -> {
                Map<String, Object> properties = new HashMap<>();
                if (!node.javaDoc().isEmpty()) {
                    properties.put("javaDoc", node.javaDoc());
                }
                return new EntryPoint(node.nodeId(), node.nodeType(), node.name(), node.fqn(), node.score(), properties);
            })
            .collect(Collectors.toList());
    }

    /**
     * Trouve les chemins entre un résultat de recherche et un nœud cible.
     * Utile pour comprendre comment deux éléments du code sont liés.
     *
     * @param sourceId      ID du nœud source
     * @param targetId      ID du nœud cible
     * @param maxPathLength Longueur maximale du chemin
     * @return Liste de chemins ordonnés par score
     * @throws SearchException Si erreur Neo4j
     */
    public List<GraphTraversal.GraphPath> findPathsBetween(
        long sourceId,
        long targetId,
        int maxPathLength
    ) throws SearchException {
        return graphTraversal.findPaths(List.of(sourceId), List.of(targetId), maxPathLength);
    }

    /**
     * Extrait le contexte graphe autour d'un point d'entrée.
     * Utile pour comprendre l'environnement d'une classe/méthode.
     *
     * @param entryPoint Point d'entrée central
     * @param radius     Rayon d'expansion (1-3 recommandé)
     * @return Sous-graphe avec nœuds triés par proximité
     * @throws SearchException Si erreur Neo4j
     */
    public GraphTraversal.Subgraph extractContext(EntryPoint entryPoint, int radius) throws SearchException {
        return graphTraversal.extractSubgraph(List.of(entryPoint.nodeId()), radius);
    }

    /**
     * Retourne les statistiques du service pour monitoring.
     */
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("graphExpansionEnabled", enableGraphExpansion);
        stats.put("llmRerankingEnabled", enableLLMReranking);
        stats.put("graphExpansionHops", graphExpansionHops);
        stats.put("hasLLMModel", llmReranker != null);
        return stats;
    }
}
