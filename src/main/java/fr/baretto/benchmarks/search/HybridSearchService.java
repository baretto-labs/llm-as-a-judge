package fr.baretto.benchmarks.search;

import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.model.embedding.EmbeddingModel;
import org.neo4j.driver.Driver;
import org.neo4j.driver.Record;
import org.neo4j.driver.Result;
import org.neo4j.driver.Session;
import org.neo4j.driver.exceptions.Neo4jException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Implémentation de recherche hybride combinant :
 * <ul>
 *   <li><b>Recherche lexicale</b> (Full-text BM25 sur name + javaDoc)</li>
 *   <li><b>Recherche vectorielle</b> (embeddings + cosine similarity)</li>
 *   <li><b>Fusion RRF</b> (Reciprocal Rank Fusion)</li>
 * </ul>
 *
 * <p><b>Architecture :</b></p>
 * <pre>
 * Query → [Étape A: Full-Text] → Top 10 lexical
 *      ↓  [Étape B: Vector]    → Top 10 vector
 *      ↓  [Étape C: RRF Fusion] → Top K final
 * </pre>
 *
 * <p><b>Prérequis Neo4j :</b></p>
 * <ul>
 *   <li>Index Full-Text sur (Class|Method).name et (Class|Method).javaDoc</li>
 *   <li>Index Vectoriel sur (Class|Method).embedding</li>
 * </ul>
 */
public class HybridSearchService implements GraphSearchHook {

    private static final Logger logger = LoggerFactory.getLogger(HybridSearchService.class);

    private static final int INTERMEDIATE_TOP_K = 10; // Top 10 pour chaque stratégie
    private static final String FULLTEXT_INDEX_NAME = "codeFullText";
    private static final String VECTOR_INDEX_NAME = "codeVector";

    private final Driver neo4jDriver;
    private final EmbeddingModel embeddingModel;
    private final int rrfK;

    /**
     * Constructeur avec configuration personnalisée.
     *
     * @param neo4jDriver    Driver Neo4j (géré par l'appelant)
     * @param embeddingModel Modèle d'embedding LangChain4j (ex: Ollama, OpenAI)
     * @param rrfK           Constante RRF (typiquement 60)
     */
    public HybridSearchService(Driver neo4jDriver, EmbeddingModel embeddingModel, int rrfK) {
        this.neo4jDriver = Objects.requireNonNull(neo4jDriver, "neo4jDriver ne peut pas être null");
        this.embeddingModel = Objects.requireNonNull(embeddingModel, "embeddingModel ne peut pas être null");
        this.rrfK = rrfK;
        logger.info("HybridSearchService initialisé (RRF k={})", rrfK);
    }

    /**
     * Constructeur avec k=60 par défaut.
     */
    public HybridSearchService(Driver neo4jDriver, EmbeddingModel embeddingModel) {
        this(neo4jDriver, embeddingModel, RRFFusion.DEFAULT_K);
    }

    @Override
    public List<EntryPoint> findEntryPoints(String query, int topK) throws SearchException {
        return findEntryPoints(query, query, topK);
    }

    /**
     * Variante avec queries séparées pour BM25 et embedding.
     * Utilisée notamment avec HyDE : bm25Query = requête naturelle originale,
     * embeddingQuery = document hypothétique généré par le LLM.
     * Évite de passer du code Java brut au parser Lucene (caractères spéciaux).
     *
     * @param bm25Query      Requête pour la recherche lexicale (langage naturel)
     * @param embeddingQuery Requête pour la recherche vectorielle (peut être un document HyDE)
     * @param topK           Nombre de résultats à retourner
     */
    public List<EntryPoint> findEntryPoints(String bm25Query, String embeddingQuery, int topK) throws SearchException {
        Objects.requireNonNull(bm25Query, "bm25Query ne peut pas être null");
        Objects.requireNonNull(embeddingQuery, "embeddingQuery ne peut pas être null");
        if (bm25Query.isBlank()) {
            throw new IllegalArgumentException("bm25Query ne peut pas être vide");
        }
        if (embeddingQuery.isBlank()) {
            throw new IllegalArgumentException("embeddingQuery ne peut pas être vide");
        }
        if (topK <= 0) {
            throw new IllegalArgumentException("topK doit être > 0");
        }

        logger.info("Recherche hybride: bm25='{}', embedding='{}...', topK={}",
            bm25Query,
            embeddingQuery.substring(0, Math.min(60, embeddingQuery.length())).replace('\n', ' '),
            topK);

        try {
            // Étape A : Recherche lexicale (Full-text BM25) — requête naturelle uniquement
            List<Long> lexicalResults = searchLexical(bm25Query, INTERMEDIATE_TOP_K);
            logger.debug("Recherche lexicale: {} résultats", lexicalResults.size());

            // Étape B : Recherche vectorielle — peut utiliser un document HyDE enrichi
            List<Long> vectorResults = searchVector(embeddingQuery, INTERMEDIATE_TOP_K);
            logger.debug("Recherche vectorielle: {} résultats", vectorResults.size());

            // Étape C : Fusion RRF
            List<Long> fusedIds = RRFFusion.fuse(
                List.of(lexicalResults, vectorResults),
                rrfK,
                topK
            );
            logger.debug("Fusion RRF: {} résultats finaux", fusedIds.size());

            // Récupérer les détails complets des nœuds fusionnés
            List<EntryPoint> entryPoints = fetchEntryPoints(fusedIds);

            logger.info("Recherche terminée: {} points d'entrée retournés", entryPoints.size());
            return entryPoints;

        } catch (Neo4jException e) {
            String msg = "Erreur Neo4j lors de la recherche: " + e.getMessage();
            logger.error(msg, e);
            throw new SearchException(msg, e);
        } catch (Exception e) {
            String msg = "Erreur inattendue lors de la recherche: " + e.getMessage();
            logger.error(msg, e);
            throw new SearchException(msg, e);
        }
    }

    /**
     * Étape A : Recherche lexicale via Full-Text Index (BM25).
     * Recherche sur les propriétés 'name' et 'javaDoc' des nœuds Class/Method.
     *
     * @param query Requête utilisateur
     * @param limit Nombre de résultats à retourner
     * @return Liste ordonnée des IDs de nœuds (meilleurs scores BM25 en premier)
     * @throws SearchException Si l'index Full-Text n'existe pas ou si la requête échoue
     */
    private List<Long> searchLexical(String query, int limit) throws SearchException {
        try (Session session = neo4jDriver.session()) {
            java.util.List<Long> allResults = new java.util.ArrayList<>();
            java.util.Map<Long, Double> scoreMap = new java.util.HashMap<>();

            // Chercher dans tous les index disponibles (Class, Method, Function)
            String[] indexNames = {FULLTEXT_INDEX_NAME, "codeFullTextMethod", "codeFullTextFunction"};
            int foundIndexes = 0;

            for (String indexName : indexNames) {
                try {
                    String cypher = String.format("""
                        CALL db.index.fulltext.queryNodes('%s', $query)
                        YIELD node, score
                        RETURN id(node) as nodeId, score
                        """, indexName);

                    Result result = session.run(cypher, Map.of("query", query));
                    result.stream().forEach(record -> {
                        long nodeId = record.get("nodeId").asLong();
                        double score = record.get("score").asDouble();

                        // Garder le meilleur score pour chaque nœud (au cas où il apparaît dans plusieurs index)
                        if (!scoreMap.containsKey(nodeId) || scoreMap.get(nodeId) < score) {
                            scoreMap.put(nodeId, score);
                            if (!allResults.contains(nodeId)) {
                                allResults.add(nodeId);
                            }
                        }
                    });
                    foundIndexes++;
                    logger.debug("Cherché dans l'index {} : {} résultats", indexName, allResults.size());
                } catch (Neo4jException e) {
                    // Index n'existe pas, continuer avec le suivant
                    logger.debug("Index {} n'existe pas ou erreur: {}", indexName, e.getMessage());
                }
            }

            if (foundIndexes == 0) {
                String msg = String.format(
                    "Aucun index Full-Text trouvé. Créez-les avec: " +
                    "CREATE FULLTEXT INDEX %s FOR (n:Class) ON EACH [n.name, n.javaDoc]",
                    FULLTEXT_INDEX_NAME
                );
                logger.error(msg);
                throw new SearchException(msg);
            }

            if (allResults.isEmpty()) {
                logger.debug("Aucun résultat lexical pour la requête: {}", query);
                return java.util.Collections.emptyList();
            }

            // Trier par score décroissant et limiter
            allResults.sort((id1, id2) -> Double.compare(scoreMap.get(id2), scoreMap.get(id1)));
            return allResults.stream().limit(limit).collect(Collectors.toList());

        } catch (SearchException e) {
            throw e;
        } catch (Exception e) {
            throw new SearchException("Erreur recherche lexicale: " + e.getMessage(), e);
        }
    }

    /**
     * Étape B : Recherche vectorielle via Vector Index.
     * Vectorise la requête avec l'EmbeddingModel, puis recherche les nœuds similaires.
     *
     * @param query Requête utilisateur
     * @param limit Nombre de résultats à retourner
     * @return Liste ordonnée des IDs de nœuds (meilleurs cosine similarity en premier)
     * @throws SearchException Si l'embedding échoue ou si l'index vectoriel n'existe pas
     */
    private List<Long> searchVector(String query, int limit) throws SearchException {
        // Vectoriser la requête avec LangChain4j
        Embedding queryEmbedding;
        try {
            queryEmbedding = embeddingModel.embed(query).content();
            logger.debug("Embedding généré: {} dimensions", queryEmbedding.vector().length);
        } catch (Exception e) {
            String msg = "Erreur lors de la génération de l'embedding (LLM indisponible ?) : " + e.getMessage();
            logger.error(msg, e);
            throw new SearchException(msg, e);
        }

        // Recherche vectorielle dans Neo4j
        try (Session session = neo4jDriver.session()) {
            java.util.List<Long> allResults = new java.util.ArrayList<>();
            java.util.Map<Long, Double> scoreMap = new java.util.HashMap<>();

            // Chercher dans tous les index disponibles (Class, Method, Function)
            String[] indexNames = {VECTOR_INDEX_NAME, "codeVectorMethod", "codeVectorFunction"};
            int foundIndexes = 0;

            for (String indexName : indexNames) {
                try {
                    String cypher = String.format("""
                        CALL db.index.vector.queryNodes('%s', $limit, $embedding)
                        YIELD node, score
                        RETURN id(node) as nodeId, score
                        """, indexName);

                    Result result = session.run(cypher, Map.of(
                        "embedding", queryEmbedding.vectorAsList(),
                        "limit", limit
                    ));

                    result.stream().forEach(record -> {
                        long nodeId = record.get("nodeId").asLong();
                        double score = record.get("score").asDouble();

                        // Garder le meilleur score pour chaque nœud
                        if (!scoreMap.containsKey(nodeId) || scoreMap.get(nodeId) < score) {
                            scoreMap.put(nodeId, score);
                            if (!allResults.contains(nodeId)) {
                                allResults.add(nodeId);
                            }
                        }
                    });
                    foundIndexes++;
                    logger.debug("Cherché dans l'index {} : {} résultats", indexName, allResults.size());
                } catch (Neo4jException e) {
                    // Index n'existe pas, continuer avec le suivant
                    logger.debug("Index {} n'existe pas ou erreur: {}", indexName, e.getMessage());
                }
            }

            if (foundIndexes == 0) {
                String msg = String.format(
                    "Aucun index Vectoriel trouvé. Créez-les avec: " +
                    "CREATE VECTOR INDEX %s FOR (n:Class) ON n.embedding " +
                    "OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}}",
                    VECTOR_INDEX_NAME
                );
                logger.error(msg);
                throw new SearchException(msg);
            }

            if (allResults.isEmpty()) {
                logger.debug("Aucun résultat vectoriel pour la requête: {}", query);
                return java.util.Collections.emptyList();
            }

            // Trier par score décroissant et limiter
            allResults.sort((id1, id2) -> Double.compare(scoreMap.get(id2), scoreMap.get(id1)));
            return allResults.stream().limit(limit).collect(Collectors.toList());

        } catch (SearchException e) {
            throw e;
        } catch (Exception e) {
            throw new SearchException("Erreur recherche vectorielle: " + e.getMessage(), e);
        }
    }

    /**
     * Récupère les détails complets des nœuds fusionnés.
     *
     * @param nodeIds Liste ordonnée des IDs (ordre = ordre RRF)
     * @return Liste d'EntryPoints avec toutes les propriétés
     */
    private List<EntryPoint> fetchEntryPoints(List<Long> nodeIds) {
        if (nodeIds.isEmpty()) {
            return List.of();
        }

        String cypher = """
            MATCH (n)
            WHERE id(n) IN $nodeIds
              AND (n:Class OR n:Function OR n:Interface OR n:Constructor OR n:Enum OR n:Record)
            RETURN id(n) as nodeId,
                   labels(n)[0] as nodeType,
                   n.name as name,
                   n.fqn as fqn,
                   n.signature as signature,
                   n.javaDoc as javaDoc,
                   n.body as body,
                   n.returnType as returnType,
                   n.visibility as visibility,
                   n.hierarchy as hierarchy
            """;

        try (Session session = neo4jDriver.session()) {
            Result result = session.run(cypher, Map.of("nodeIds", nodeIds));

            // Créer une map pour conserver l'ordre RRF
            Map<Long, EntryPoint> entryPointMap = result.stream()
                .map(this::recordToEntryPoint)
                .collect(Collectors.toMap(
                    EntryPoint::nodeId,
                    ep -> ep,
                    (e1, e2) -> e1
                ));

            // Retourner dans l'ordre RRF avec scores calculés
            List<EntryPoint> orderedResults = new ArrayList<>();
            for (int i = 0; i < nodeIds.size(); i++) {
                long nodeId = nodeIds.get(i);
                EntryPoint ep = entryPointMap.get(nodeId);
                if (ep != null) {
                    // Score basé sur la position RRF (décroissant)
                    double rrfScore = 1.0 / (rrfK + i + 1);
                    EntryPoint withScore = new EntryPoint(
                        ep.nodeId(),
                        ep.nodeType(),
                        ep.name(),
                        ep.fqn(),
                        rrfScore,
                        ep.properties()
                    );
                    orderedResults.add(withScore);
                }
            }

            return orderedResults;
        }
    }

    /**
     * Convertit un Record Neo4j en EntryPoint.
     */
    private EntryPoint recordToEntryPoint(Record record) {
        long nodeId = record.get("nodeId").asLong();
        String nodeType = record.get("nodeType").asString("Unknown");
        String name = record.get("name").asString("(unnamed)");
        String fqn = record.get("fqn").asString(name);

        Map<String, Object> properties = new HashMap<>();
        if (!record.get("signature").isNull()) {
            properties.put("signature", record.get("signature").asString());
        }
        if (!record.get("javaDoc").isNull()) {
            properties.put("javaDoc", record.get("javaDoc").asString());
        }
        if (!record.get("body").isNull()) {
            properties.put("body", record.get("body").asString());
        }
        if (!record.get("returnType").isNull()) {
            properties.put("returnType", record.get("returnType").asString());
        }
        if (!record.get("visibility").isNull()) {
            properties.put("visibility", record.get("visibility").asString());
        }
        if (!record.get("hierarchy").isNull()) {
            properties.put("hierarchy", record.get("hierarchy").asString());
        }

        return new EntryPoint(nodeId, nodeType, name, fqn, 0.0, properties);
    }
}
