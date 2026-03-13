package fr.baretto.benchmarks.search;

/**
 * Résultat intermédiaire d'une recherche (lexicale ou vectorielle).
 * Utilisé avant la fusion RRF.
 *
 * @param nodeId Identifiant unique du nœud Neo4j
 * @param rank   Rang du résultat dans la liste (1 = premier, 2 = deuxième, etc.)
 * @param score  Score brut de la recherche (BM25 pour lexical, cosine similarity pour vectoriel)
 */
record SearchResult(
    long nodeId,
    int rank,
    double score
) implements Comparable<SearchResult> {

    /**
     * Compare les SearchResults par score décroissant.
     */
    @Override
    public int compareTo(SearchResult other) {
        return Double.compare(other.score, this.score);
    }
}
