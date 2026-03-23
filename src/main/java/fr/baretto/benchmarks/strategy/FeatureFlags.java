package fr.baretto.benchmarks.strategy;

/**
 * Feature flags pour configurer progressivement les optimisations RAG.
 *
 * <p>Permet de feature-flipper chaque couche d'amélioration et de mesurer sa valeur marginale :</p>
 * <ul>
 *   <li>{@code knn-only}          — KNN vectoriel pur (baseline, top-5)</li>
 *   <li>{@code hybrid}            — BM25 + KNN + RRF (top-10, applicable aux deux stratégies)</li>
 *   <li>{@code hybrid-graph}      — hybrid + expansion K-hop (Neo4j seulement)</li>
 *   <li>{@code hybrid-graph-hyde} — hybrid-graph + HyDE query expansion</li>
 *   <li>{@code full}              — hybrid-graph-hyde + LLM reranking</li>
 * </ul>
 *
 * <p>Usage benchmark : {@code @Param({"knn-only|hybrid", "hybrid|hybrid-graph"})}</p>
 *
 * @param bm25Enabled           Active la recherche full-text BM25
 * @param rrfEnabled            Active la fusion RRF (requiert bm25Enabled)
 * @param graphExpansionEnabled Active l'expansion K-hop (Neo4j uniquement)
 * @param hydeEnabled           Active HyDE query expansion (Neo4j uniquement)
 * @param rerankingEnabled      Active le LLM reranking (Neo4j uniquement)
 * @param topK                  Nombre de résultats à retourner
 * @param kHops                 Profondeur d'expansion K-hop
 * @param rrfK                  Constante RRF (défaut : 60, standard TREC)
 */
public record FeatureFlags(
        boolean bm25Enabled,
        boolean rrfEnabled,
        boolean graphExpansionEnabled,
        boolean hydeEnabled,
        boolean rerankingEnabled,
        int topK,
        int kHops,
        int rrfK
) {

    /** Valeur par défaut de la constante RRF (standard TREC, Sweet spot empirique). */
    public static final int DEFAULT_RRF_K = 60;

    // ── Presets ──────────────────────────────────────────────────────────────

    /** KNN vectoriel pur — baseline Lucene (top-5, pas de BM25, pas de RRF). */
    public static FeatureFlags knnOnly() {
        return new FeatureFlags(false, false, false, false, false, 5, 0, DEFAULT_RRF_K);
    }

    /**
     * BM25 + KNN + RRF — pipeline hybride de base.
     * Applicable aux deux stratégies : isole la valeur du graphe.
     */
    public static FeatureFlags hybrid() {
        return new FeatureFlags(true, true, false, false, false, 10, 0, DEFAULT_RRF_K);
    }

    /** hybrid + expansion K-hop (1 saut) — valeur marginale du graphe. */
    public static FeatureFlags hybridGraph() {
        return new FeatureFlags(true, true, true, false, false, 10, 1, DEFAULT_RRF_K);
    }

    /** hybridGraph + HyDE query expansion — valeur marginale de HyDE. */
    public static FeatureFlags hybridGraphHyde() {
        return new FeatureFlags(true, true, true, true, false, 10, 1, DEFAULT_RRF_K);
    }

    /** Pipeline GraphRAG complet incluant LLM reranking. */
    public static FeatureFlags full() {
        return new FeatureFlags(true, true, true, true, true, 10, 1, DEFAULT_RRF_K);
    }

    // ── Parsing ──────────────────────────────────────────────────────────────

    /**
     * Crée un {@code FeatureFlags} à partir d'un nom de preset.
     *
     * @param preset Nom du preset ({@code knn-only}, {@code hybrid}, {@code hybrid-graph},
     *               {@code hybrid-graph-hyde}, {@code full})
     * @throws IllegalArgumentException si le preset est inconnu
     */
    public static FeatureFlags fromPreset(String preset) {
        return switch (preset.trim().toLowerCase()) {
            case "knn-only"          -> knnOnly();
            case "hybrid"            -> hybrid();
            case "hybrid-graph"      -> hybridGraph();
            case "hybrid-graph-hyde" -> hybridGraphHyde();
            case "full"              -> full();
            default -> throw new IllegalArgumentException(
                "Preset inconnu: '" + preset + "'. Valeurs valides: knn-only, hybrid, hybrid-graph, hybrid-graph-hyde, full");
        };
    }

    /** Nom lisible du preset courant (pour {@code getStrategyName()}). */
    public String presetName() {
        if (!bm25Enabled) return "knn-only";
        if (!graphExpansionEnabled) return "hybrid";
        if (!hydeEnabled) return "hybrid-graph";
        if (!rerankingEnabled) return "hybrid-graph-hyde";
        return "full";
    }
}
