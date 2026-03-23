package fr.baretto.benchmarks.search;

import org.neo4j.driver.Driver;
import org.neo4j.driver.Record;
import org.neo4j.driver.Result;
import org.neo4j.driver.Session;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Utilitaires pour la traversée de graphe et l'expansion de contexte.
 * <p>
 * Implémente les patterns GraphRAG avancés :
 * <ul>
 *   <li><b>K-hop expansion</b> : Trouve les voisins à K sauts d'un nœud</li>
 *   <li><b>Path ranking</b> : Classe les chemins par pertinence</li>
 *   <li><b>Subgraph extraction</b> : Extrait un sous-graphe autour de nœuds</li>
 * </ul>
 *
 * <p><b>Patterns de relations supportés</b> :</p>
 * <ul>
 *   <li>CALLS : Appels de méthodes</li>
 *   <li>DECLARES : Déclarations (class → method)</li>
 *   <li>USES : Utilisation de types</li>
 *   <li>RETURNS : Type de retour</li>
 *   <li>EXTENDS : Héritage</li>
 *   <li>IMPLEMENTS : Interfaces</li>
 * </ul>
 */
public class GraphTraversal {

    private static final Logger logger = LoggerFactory.getLogger(GraphTraversal.class);

    private final Driver neo4jDriver;

    // Poids des relations pour ranking
    private static final Map<String, Double> RELATION_WEIGHTS = Map.of(
        "CALLS", 1.0,      // Appels directs = très pertinents
        "DECLARES", 0.8,   // Déclarations = pertinent
        "USES", 0.6,       // Utilisation = moyennement pertinent
        "RETURNS", 0.5,    // Type retour = contexte
        "EXTENDS", 0.7,    // Héritage = important
        "IMPLEMENTS", 0.7  // Interface = important
    );

    public GraphTraversal(Driver neo4jDriver) {
        this.neo4jDriver = neo4jDriver;
    }

    /**
     * Expanse K-hop à partir de nœuds initiaux.
     * <p>
     * Trouve tous les nœuds accessibles en K sauts maximum depuis les nœuds de départ,
     * en suivant les relations spécifiées.
     *
     * @param initialNodeIds IDs des nœuds de départ
     * @param maxHops Nombre maximum de sauts (1-3 recommandé)
     * @param relationTypes Types de relations à suivre (null = toutes)
     * @return Map nodeId → distance (hop count)
     * @throws SearchException Si erreur Neo4j
     */
    public Map<Long, Integer> expandKHop(
        List<Long> initialNodeIds,
        int maxHops,
        List<String> relationTypes
    ) throws SearchException {

        if (initialNodeIds == null || initialNodeIds.isEmpty()) {
            return Map.of();
        }

        if (maxHops < 1 || maxHops > 5) {
            throw new IllegalArgumentException("maxHops doit être entre 1 et 5");
        }

        String relationFilter = buildRelationFilter(relationTypes);

        String cypher = String.format("""
            MATCH (initial)
            WHERE id(initial) IN $nodeIds
            CALL {
                WITH initial
                MATCH path = (initial)-[%s*1..%d]-(related)
                WHERE related:Class OR related:Function OR related:Interface
                   OR related:Constructor OR related:Enum OR related:Record
                RETURN DISTINCT related as node, length(path) as distance
            }
            RETURN id(node) as nodeId, min(distance) as minDistance
            ORDER BY minDistance ASC
            """, relationFilter, maxHops);

        try (Session session = neo4jDriver.session()) {
            Result result = session.run(cypher, Map.of("nodeIds", initialNodeIds));

            Map<Long, Integer> expansionMap = new HashMap<>();
            result.stream().forEach(record -> {
                long nodeId = record.get("nodeId").asLong();
                int distance = record.get("minDistance").asInt();
                expansionMap.put(nodeId, distance);
            });

            logger.debug("K-hop expansion: {} nœuds initiaux → {} nœuds à {} hops max",
                initialNodeIds.size(), expansionMap.size(), maxHops);

            return expansionMap;

        } catch (Exception e) {
            throw new SearchException("Erreur lors de l'expansion K-hop: " + e.getMessage(), e);
        }
    }

    /**
     * Trouve les chemins entre deux ensembles de nœuds.
     * <p>
     * Utile pour comprendre comment deux entités sont liées (ex: comment authenticate() utilise UserRepository).
     *
     * @param sourceIds IDs des nœuds sources
     * @param targetIds IDs des nœuds cibles
     * @param maxPathLength Longueur maximale des chemins (1-4 recommandé)
     * @return Liste de chemins avec leur score
     * @throws SearchException Si erreur Neo4j
     */
    public List<GraphPath> findPaths(
        List<Long> sourceIds,
        List<Long> targetIds,
        int maxPathLength
    ) throws SearchException {

        if (sourceIds == null || sourceIds.isEmpty() || targetIds == null || targetIds.isEmpty()) {
            return List.of();
        }

        if (maxPathLength < 1 || maxPathLength > 6) {
            throw new IllegalArgumentException("maxPathLength doit être entre 1 et 6");
        }

        String cypher = """
            MATCH (source), (target)
            WHERE id(source) IN $sourceIds AND id(target) IN $targetIds
            MATCH path = shortestPath((source)-[*1..%d]-(target))
            WHERE ALL(rel IN relationships(path) WHERE type(rel) IN ['CALLS', 'DECLARES', 'USES', 'RETURNS', 'EXTENDS', 'IMPLEMENTS'])
            RETURN
                id(source) as sourceId,
                id(target) as targetId,
                [node IN nodes(path) | id(node)] as nodeIds,
                [rel IN relationships(path) | type(rel)] as relationTypes,
                length(path) as pathLength
            ORDER BY pathLength ASC
            LIMIT 20
            """.formatted(maxPathLength);

        try (Session session = neo4jDriver.session()) {
            Result result = session.run(cypher, Map.of(
                "sourceIds", sourceIds,
                "targetIds", targetIds
            ));

            List<GraphPath> paths = result.stream()
                .map(this::recordToPath)
                .sorted(Comparator.comparingDouble(GraphPath::score).reversed())
                .collect(Collectors.toList());

            logger.debug("Trouvé {} chemins entre {} sources et {} targets",
                paths.size(), sourceIds.size(), targetIds.size());

            return paths;

        } catch (Exception e) {
            throw new SearchException("Erreur lors de la recherche de chemins: " + e.getMessage(), e);
        }
    }

    /**
     * Extrait un sous-graphe autour de nœuds centraux.
     * <p>
     * Retourne tous les nœuds et relations dans un rayon de K sauts,
     * avec scores basés sur la distance et le type de relation.
     *
     * @param centralNodeIds IDs des nœuds centraux
     * @param radius Rayon d'extraction (1-3 recommandé)
     * @return Sous-graphe avec nœuds scorés
     * @throws SearchException Si erreur Neo4j
     */
    public Subgraph extractSubgraph(
        List<Long> centralNodeIds,
        int radius
    ) throws SearchException {

        if (centralNodeIds == null || centralNodeIds.isEmpty()) {
            return new Subgraph(List.of(), Map.of());
        }

        if (radius < 1 || radius > 3) {
            throw new IllegalArgumentException("radius doit être entre 1 et 3");
        }

        // Étape 1: Expansion K-hop
        Map<Long, Integer> expandedNodes = expandKHop(
            centralNodeIds,
            radius,
            List.of("CALLS", "DECLARES", "USES", "RETURNS", "EXTENDS", "IMPLEMENTS")
        );

        // Étape 2: Récupérer détails des nœuds
        List<Long> allNodeIds = new ArrayList<>(expandedNodes.keySet());
        allNodeIds.addAll(centralNodeIds); // Inclure centraux

        String cypher = """
            MATCH (n)
            WHERE id(n) IN $nodeIds
            RETURN
                id(n)          AS nodeId,
                labels(n)[0]   AS nodeType,
                n.name         AS name,
                n.fqn          AS fqn,
                n.javaDoc      AS javaDoc,
                n.body         AS body,
                n.signature    AS signature,
                n.returnType   AS returnType,
                n.visibility   AS visibility,
                n.hierarchy    AS hierarchy
            """;

        try (Session session = neo4jDriver.session()) {
            Result result = session.run(cypher, Map.of("nodeIds", allNodeIds));

            List<SubgraphNode> nodes = result.stream()
                .map(record -> {
                    long nodeId = record.get("nodeId").asLong();
                    int distance = expandedNodes.getOrDefault(nodeId, 0);
                    double score = 1.0 / (1.0 + distance);
                    String javaDoc = record.get("javaDoc").isNull() ? "" : record.get("javaDoc").asString();

                    Map<String, Object> props = new HashMap<>();
                    if (!record.get("body").isNull())       props.put("body",       record.get("body").asString());
                    if (!record.get("signature").isNull())  props.put("signature",  record.get("signature").asString());
                    if (!record.get("returnType").isNull()) props.put("returnType", record.get("returnType").asString());
                    if (!record.get("visibility").isNull()) props.put("visibility", record.get("visibility").asString());
                    if (!record.get("hierarchy").isNull())  props.put("hierarchy",  record.get("hierarchy").asString());
                    if (!javaDoc.isBlank())                 props.put("javaDoc",    javaDoc);

                    return new SubgraphNode(nodeId, record.get("nodeType").asString(),
                        record.get("name").asString(), record.get("fqn").asString(""),
                        javaDoc, distance, score, props);
                })
                .collect(Collectors.toList());

            logger.debug("Subgraph extrait: {} nœuds centraux → {} nœuds totaux (radius={})",
                centralNodeIds.size(), nodes.size(), radius);

            return new Subgraph(nodes, expandedNodes);

        } catch (Exception e) {
            throw new SearchException("Erreur lors de l'extraction du sous-graphe: " + e.getMessage(), e);
        }
    }

    /**
     * Récupère les détails de nœuds par IDs sans expansion.
     *
     * @param nodeIds IDs des nœuds à récupérer
     * @param distanceMap Map nodeId → distance (pour le calcul du score)
     * @return Liste de SubgraphNode avec propriétés et scores
     * @throws SearchException Si erreur Neo4j
     */
    public List<SubgraphNode> fetchNodes(
        List<Long> nodeIds,
        Map<Long, Integer> distanceMap
    ) throws SearchException {
        if (nodeIds == null || nodeIds.isEmpty()) {
            return List.of();
        }

        String cypher = """
            MATCH (n)
            WHERE id(n) IN $nodeIds
            RETURN
                id(n)          AS nodeId,
                labels(n)[0]   AS nodeType,
                n.name         AS name,
                n.fqn          AS fqn,
                n.javaDoc      AS javaDoc,
                n.body         AS body,
                n.signature    AS signature,
                n.returnType   AS returnType,
                n.visibility   AS visibility,
                n.hierarchy    AS hierarchy
            """;

        try (Session session = neo4jDriver.session()) {
            Result result = session.run(cypher, Map.of("nodeIds", nodeIds));

            return result.stream()
                .map(record -> {
                    long nodeId = record.get("nodeId").asLong();
                    int distance = distanceMap.getOrDefault(nodeId, 0);
                    double score = 1.0 / (1.0 + distance);
                    String javaDoc = record.get("javaDoc").isNull() ? "" : record.get("javaDoc").asString();

                    Map<String, Object> props = new HashMap<>();
                    if (!record.get("body").isNull())       props.put("body",       record.get("body").asString());
                    if (!record.get("signature").isNull())  props.put("signature",  record.get("signature").asString());
                    if (!record.get("returnType").isNull()) props.put("returnType", record.get("returnType").asString());
                    if (!record.get("visibility").isNull()) props.put("visibility", record.get("visibility").asString());
                    if (!record.get("hierarchy").isNull())  props.put("hierarchy",  record.get("hierarchy").asString());
                    if (!javaDoc.isBlank())                 props.put("javaDoc",    javaDoc);

                    return new SubgraphNode(nodeId, record.get("nodeType").asString(),
                        record.get("name").asString(), record.get("fqn").asString(""),
                        javaDoc, distance, score, props);
                })
                .collect(Collectors.toList());

        } catch (Exception e) {
            throw new SearchException("Erreur lors de la récupération des nœuds: " + e.getMessage(), e);
        }
    }

    /**
     * Construit le filtre de relations pour Cypher.
     */
    private String buildRelationFilter(List<String> relationTypes) {
        if (relationTypes == null || relationTypes.isEmpty()) {
            return ""; // Toutes relations
        }
        return ":" + String.join("|", relationTypes);
    }

    /**
     * Convertit un Record Neo4j en GraphPath.
     */
    private GraphPath recordToPath(Record record) {
        long sourceId = record.get("sourceId").asLong();
        long targetId = record.get("targetId").asLong();

        List<Long> nodeIds = record.get("nodeIds").asList(value -> value.asLong());
        List<String> relationTypes = record.get("relationTypes").asList(value -> value.asString());
        int pathLength = record.get("pathLength").asInt();

        // Calculer score basé sur longueur et types de relations
        double score = calculatePathScore(pathLength, relationTypes);

        return new GraphPath(sourceId, targetId, nodeIds, relationTypes, pathLength, score);
    }

    /**
     * Calcule le score d'un chemin basé sur sa longueur et ses relations.
     * <p>
     * Score élevé = chemin court avec relations pertinentes.
     */
    private double calculatePathScore(int length, List<String> relationTypes) {
        // Score de base : inverse de la longueur
        double baseScore = 1.0 / (1.0 + length);

        // Bonus pour relations pertinentes
        double relationBonus = relationTypes.stream()
            .mapToDouble(type -> RELATION_WEIGHTS.getOrDefault(type, 0.3))
            .average()
            .orElse(0.5);

        return baseScore * relationBonus;
    }

    /**
     * Représente un chemin dans le graphe.
     */
    public record GraphPath(
        long sourceId,
        long targetId,
        List<Long> nodeIds,
        List<String> relationTypes,
        int length,
        double score
    ) implements Comparable<GraphPath> {
        @Override
        public int compareTo(GraphPath other) {
            return Double.compare(other.score, this.score); // Décroissant
        }
    }

    /**
     * Représente un sous-graphe extrait.
     */
    public record Subgraph(
        List<SubgraphNode> nodes,
        Map<Long, Integer> distanceMap
    ) {
        /**
         * Filtre les nœuds par distance maximale.
         */
        public List<SubgraphNode> filterByDistance(int maxDistance) {
            return nodes.stream()
                .filter(node -> node.distance <= maxDistance)
                .collect(Collectors.toList());
        }

        /**
         * Retourne les nœuds triés par score décroissant.
         */
        public List<SubgraphNode> sortedByScore() {
            return nodes.stream()
                .sorted(Comparator.comparingDouble(SubgraphNode::score).reversed())
                .collect(Collectors.toList());
        }
    }

    /**
     * Représente un nœud dans un sous-graphe.
     * {@code properties} contient toutes les propriétés scalaires du nœud
     * (body, signature, returnType, visibility, hierarchy, javaDoc…).
     */
    public record SubgraphNode(
        long nodeId,
        String nodeType,
        String name,
        String fqn,
        String javaDoc,
        int distance,
        double score,
        Map<String, Object> properties
    ) implements Comparable<SubgraphNode> {

        /** Constructeur de compatibilité (sans propriétés étendues). */
        public SubgraphNode(long nodeId, String nodeType, String name, String fqn,
                            String javaDoc, int distance, double score) {
            this(nodeId, nodeType, name, fqn, javaDoc, distance, score, Map.of());
        }

        @Override
        public int compareTo(SubgraphNode other) {
            return Double.compare(other.score, this.score); // Décroissant
        }
    }
}
