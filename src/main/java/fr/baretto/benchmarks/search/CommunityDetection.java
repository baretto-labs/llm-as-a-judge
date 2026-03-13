package fr.baretto.benchmarks.search;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.input.Prompt;
import dev.langchain4j.model.input.PromptTemplate;
import org.neo4j.driver.Driver;
import org.neo4j.driver.Record;
import org.neo4j.driver.Result;
import org.neo4j.driver.Session;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

/**
 * Détection de communautés dans le graphe de code.
 * <p>
 * Implémente un algorithme simplifié de détection de clusters basé sur:
 * <ul>
 *   <li><b>Composantes connexes</b> : Groupes de nœuds fortement liés</li>
 *   <li><b>Modularité</b> : Densité de connexions internes vs externes</li>
 *   <li><b>Résumés LLM</b> : Génération de descriptions high-level</li>
 * </ul>
 *
 * <p><b>Note</b> : Cette implémentation utilise Cypher natif pour compatibilité maximale.
 * Pour de meilleures performances sur grands graphes, utiliser Neo4j GDS (Graph Data Science).</p>
 */
public class CommunityDetection {

    private static final Logger logger = LoggerFactory.getLogger(CommunityDetection.class);

    private final Driver neo4jDriver;
    private final ChatModel llmModel; // Optionnel, pour résumés

    public CommunityDetection(Driver neo4jDriver, ChatModel llmModel) {
        this.neo4jDriver = neo4jDriver;
        this.llmModel = llmModel;
    }

    public CommunityDetection(Driver neo4jDriver) {
        this(neo4jDriver, null);
    }

    /**
     * Détecte les communautés (clusters) dans le graphe.
     * <p>
     * Algorithme simplifié basé sur la propagation de labels :
     * 1. Chaque nœud commence avec son propre label (communauté)
     * 2. Itérativement, chaque nœud adopte le label le plus fréquent parmi ses voisins
     * 3. Convergence après K itérations
     *
     * @param minCommunitySize Taille minimale d'une communauté (défaut: 3)
     * @param maxIterations Nombre maximum d'itérations (défaut: 10)
     * @return Liste des communautés détectées
     * @throws SearchException Si erreur Neo4j
     */
    public List<Community> detectCommunities(
        int minCommunitySize,
        int maxIterations
    ) throws SearchException {

        if (minCommunitySize < 1) {
            throw new IllegalArgumentException("minCommunitySize doit être >= 1");
        }

        if (maxIterations < 1 || maxIterations > 50) {
            throw new IllegalArgumentException("maxIterations doit être entre 1 et 50");
        }

        try (Session session = neo4jDriver.session()) {

            // Étape 1: Initialiser chaque nœud avec son propre ID comme communauté
            session.run("""
                MATCH (n)
                WHERE n:Class OR n:Method OR n:Function OR n:Interface
                SET n.communityId = id(n)
                """);

            // Étape 2: Propagation de labels (itératif)
            for (int i = 0; i < maxIterations; i++) {
                Result result = session.run("""
                    MATCH (n)-[r:CALLS|DECLARES|USES|EXTENDS|IMPLEMENTS]-(neighbor)
                    WHERE n.communityId IS NOT NULL AND neighbor.communityId IS NOT NULL
                    WITH n, neighbor.communityId as neighborCommunity
                    WITH n, neighborCommunity, count(*) as frequency
                    ORDER BY frequency DESC
                    WITH n, collect(neighborCommunity)[0] as mostFrequentCommunity
                    SET n.communityId = mostFrequentCommunity
                    RETURN count(n) as updated
                    """);

                long updated = result.single().get("updated").asLong();
                logger.debug("Itération {}: {} nœuds mis à jour", i + 1, updated);

                // Convergence si aucun changement
                if (updated == 0) {
                    logger.info("Convergence atteinte après {} itérations", i + 1);
                    break;
                }
            }

            // Étape 3: Récupérer les communautés
            Result communitiesResult = session.run("""
                MATCH (n)
                WHERE n.communityId IS NOT NULL
                WITH n.communityId as communityId, collect(n) as nodes
                WHERE size(nodes) >= $minSize
                RETURN
                    communityId,
                    [node IN nodes | id(node)] as nodeIds,
                    [node IN nodes | labels(node)[0]] as nodeTypes,
                    [node IN nodes | node.name] as nodeNames,
                    [node IN nodes | coalesce(node.fqn, '')] as nodeFqns,
                    [node IN nodes | coalesce(node.javaDoc, '')] as nodeJavaDocs,
                    size(nodes) as size
                ORDER BY size DESC
                """, Map.of("minSize", minCommunitySize));

            List<Community> communities = new ArrayList<>();
            AtomicInteger communityIndex = new AtomicInteger(1);

            communitiesResult.stream().forEach(record -> {
                long communityId = record.get("communityId").asLong();
                List<Long> nodeIds = record.get("nodeIds").asList(v -> v.asLong());
                List<String> nodeTypes = record.get("nodeTypes").asList(v -> v.asString());
                List<String> nodeNames = record.get("nodeNames").asList(v -> v.asString());
                List<String> nodeFqns = record.get("nodeFqns").asList(v -> v.asString());
                List<String> nodeJavaDocs = record.get("nodeJavaDocs").asList(v -> v.asString());
                int size = record.get("size").asInt();

                // Construire les nœuds de la communauté
                List<CommunityNode> nodes = new ArrayList<>();
                for (int i = 0; i < nodeIds.size(); i++) {
                    nodes.add(new CommunityNode(
                        nodeIds.get(i),
                        nodeTypes.get(i),
                        nodeNames.get(i),
                        nodeFqns.get(i),
                        nodeJavaDocs.get(i)
                    ));
                }

                Community community = new Community(
                    communityId,
                    "Community " + communityIndex.get(),
                    nodes,
                    size,
                    null // Summary sera généré plus tard si LLM disponible
                );

                communities.add(community);
                communityIndex.incrementAndGet();
            });

            logger.info("Détecté {} communautés (taille min: {})", communities.size(), minCommunitySize);

            // Étape 4: Générer résumés LLM si disponible
            if (llmModel != null) {
                for (Community community : communities) {
                    String summary = generateCommunitySummary(community);
                    community.setSummary(summary);
                }
            }

            return communities;

        } catch (Exception e) {
            throw new SearchException("Erreur lors de la détection de communautés: " + e.getMessage(), e);
        }
    }

    /**
     * Génère un résumé textuel d'une communauté via LLM.
     * <p>
     * Utilise les noms, FQNs et JavaDocs des nœuds pour créer un résumé high-level.
     *
     * @param community La communauté à résumer
     * @return Résumé textuel (2-3 phrases)
     */
    private String generateCommunitySummary(Community community) {
        if (llmModel == null) {
            return "Résumé non disponible (LLM non configuré)";
        }

        try {
            // Construire le contexte de la communauté
            StringBuilder context = new StringBuilder();
            context.append("Classes:\n");

            List<CommunityNode> classes = community.nodes().stream()
                .filter(n -> n.nodeType().equals("Class"))
                .limit(10) // Limiter pour ne pas dépasser context window
                .collect(Collectors.toList());

            for (CommunityNode node : classes) {
                context.append("- ").append(node.name());
                if (!node.javaDoc().isEmpty()) {
                    context.append(": ").append(node.javaDoc().substring(0, Math.min(100, node.javaDoc().length())));
                }
                context.append("\n");
            }

            context.append("\nMéthodes clés:\n");
            List<CommunityNode> methods = community.nodes().stream()
                .filter(n -> n.nodeType().equals("Method") || n.nodeType().equals("Function"))
                .limit(10)
                .collect(Collectors.toList());

            for (CommunityNode node : methods) {
                context.append("- ").append(node.name()).append("\n");
            }

            // Prompt LLM
            PromptTemplate template = PromptTemplate.from("""
                Voici un cluster de code Java contenant {{classCount}} classes et {{methodCount}} méthodes.

                {{context}}

                Génère un résumé en 2-3 phrases maximum décrivant le rôle fonctionnel de ce module.
                Sois concis et précis. Évite les détails techniques inutiles.
                """);

            Prompt prompt = template.apply(Map.of(
                "classCount", classes.size(),
                "methodCount", methods.size(),
                "context", context.toString()
            ));

            String summary = llmModel.chat(prompt.text());

            logger.debug("Résumé LLM généré pour communauté {} ({} caractères)",
                community.name(), summary.length());

            return summary.trim();

        } catch (Exception e) {
            logger.warn("Erreur génération résumé LLM pour communauté {}: {}",
                community.name(), e.getMessage());
            return "Groupe de " + community.size() + " éléments liés";
        }
    }

    /**
     * Recherche dans les communautés (global search).
     * <p>
     * Trouve les communautés dont le résumé ou les nœuds matchent la requête.
     *
     * @param communities Liste des communautés
     * @param query Requête utilisateur
     * @param topK Nombre de communautés à retourner
     * @return Communautés classées par pertinence
     */
    public List<Community> searchCommunities(
        List<Community> communities,
        String query,
        int topK
    ) {
        if (query == null || query.isBlank()) {
            return communities.stream().limit(topK).collect(Collectors.toList());
        }

        String queryLower = query.toLowerCase();

        // Scorer chaque communauté
        List<ScoredCommunity> scored = communities.stream()
            .map(community -> {
                double score = 0.0;

                // Match sur résumé (poids fort)
                if (community.summary() != null && community.summary().toLowerCase().contains(queryLower)) {
                    score += 10.0;
                }

                // Match sur nom de communauté
                if (community.name().toLowerCase().contains(queryLower)) {
                    score += 5.0;
                }

                // Match sur noms de classes (poids moyen)
                long classMatches = community.nodes().stream()
                    .filter(n -> n.nodeType().equals("Class"))
                    .filter(n -> n.name().toLowerCase().contains(queryLower))
                    .count();
                score += classMatches * 2.0;

                // Match sur FQNs ou JavaDocs (poids faible)
                long docMatches = community.nodes().stream()
                    .filter(n -> n.javaDoc().toLowerCase().contains(queryLower) ||
                                 n.fqn().toLowerCase().contains(queryLower))
                    .count();
                score += docMatches * 0.5;

                return new ScoredCommunity(community, score);
            })
            .filter(sc -> sc.score > 0)
            .sorted(Comparator.comparingDouble(ScoredCommunity::score).reversed())
            .collect(Collectors.toList());

        return scored.stream()
            .limit(topK)
            .map(ScoredCommunity::community)
            .collect(Collectors.toList());
    }

    /**
     * Représente une communauté (cluster) de nœuds.
     */
    public static class Community {
        private final long id;
        private final String name;
        private final List<CommunityNode> nodes;
        private final int size;
        private String summary; // Mutable pour lazy generation

        public Community(long id, String name, List<CommunityNode> nodes, int size, String summary) {
            this.id = id;
            this.name = name;
            this.nodes = nodes;
            this.size = size;
            this.summary = summary;
        }

        public long id() { return id; }
        public String name() { return name; }
        public List<CommunityNode> nodes() { return nodes; }
        public int size() { return size; }
        public String summary() { return summary; }

        public void setSummary(String summary) {
            this.summary = summary;
        }

        /**
         * Retourne les classes principales de la communauté.
         */
        public List<CommunityNode> getClasses() {
            return nodes.stream()
                .filter(n -> n.nodeType().equals("Class"))
                .collect(Collectors.toList());
        }

        /**
         * Retourne les méthodes de la communauté.
         */
        public List<CommunityNode> getMethods() {
            return nodes.stream()
                .filter(n -> n.nodeType().equals("Method") || n.nodeType().equals("Function"))
                .collect(Collectors.toList());
        }

        @Override
        public String toString() {
            return String.format("Community{name='%s', size=%d, classes=%d, methods=%d}",
                name, size, getClasses().size(), getMethods().size());
        }
    }

    /**
     * Représente un nœud dans une communauté.
     */
    public record CommunityNode(
        long nodeId,
        String nodeType,
        String name,
        String fqn,
        String javaDoc
    ) {}

    /**
     * Communauté avec score (pour recherche).
     */
    private record ScoredCommunity(
        Community community,
        double score
    ) {}
}
