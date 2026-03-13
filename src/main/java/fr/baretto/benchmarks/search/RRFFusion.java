package fr.baretto.benchmarks.search;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Implémentation de l'algorithme RRF (Reciprocal Rank Fusion).
 *
 * <p><b>Principe mathématique :</b><br>
 * RRF combine plusieurs listes de résultats classés en attribuant à chaque élément un score
 * basé sur sa position dans chaque liste. La formule est :
 *
 * <pre>
 * score_RRF(item) = Σ ( 1 / (k + rank_i) )
 * </pre>
 *
 * où :
 * <ul>
 *   <li><b>rank_i</b> : position de l'item dans la liste i (1 pour le premier, 2 pour le deuxième, etc.)</li>
 *   <li><b>k</b> : constante de régularisation (typiquement 60)</li>
 * </ul>
 *
 * <p><b>Propriétés de RRF :</b></p>
 * <ul>
 *   <li>Favorise les items bien classés dans <b>plusieurs</b> listes</li>
 *   <li>Robuste aux outliers (un item très bien classé dans une seule liste ne domine pas)</li>
 *   <li>Ne nécessite pas de normalisation des scores bruts</li>
 *   <li>Indépendant de l'échelle des scores originaux</li>
 * </ul>
 *
 * <p><b>Exemple :</b></p>
 * <pre>
 * Liste A (lexical) : [item1, item2, item3]
 * Liste B (vector)  : [item3, item1, item4]
 *
 * Scores RRF (k=60) :
 *   item1 : 1/(60+1) + 1/(60+2) ≈ 0.0326
 *   item2 : 1/(60+2)            ≈ 0.0161
 *   item3 : 1/(60+3) + 1/(60+1) ≈ 0.0323
 *   item4 : 1/(60+3)            ≈ 0.0159
 *
 * Classement final : [item1, item3, item2, item4]
 * </pre>
 *
 * @see <a href="https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf">Original RRF Paper</a>
 */
public final class RRFFusion {

    /**
     * Constante de régularisation par défaut (valeur standard de la littérature).
     */
    public static final int DEFAULT_K = 60;

    /**
     * Classe non-instanciable (utilitaire pur).
     */
    private RRFFusion() {
        throw new UnsupportedOperationException("Utility class");
    }

    /**
     * Fusionne plusieurs listes de résultats classés en utilisant RRF.
     *
     * @param rankedLists Liste de listes classées (chaque liste représente les résultats d'une stratégie)
     * @param k           Constante de régularisation RRF (typiquement 60)
     * @param topK        Nombre de résultats à retourner
     * @return Liste fusionnée des Top K résultats, ordonnée par score RRF décroissant
     * @throws IllegalArgumentException Si rankedLists est vide ou topK <= 0
     */
    public static List<Long> fuse(List<List<Long>> rankedLists, int k, int topK) {
        if (rankedLists == null || rankedLists.isEmpty()) {
            throw new IllegalArgumentException("rankedLists ne peut pas être vide");
        }
        if (topK <= 0) {
            throw new IllegalArgumentException("topK doit être > 0");
        }

        // Map: nodeId → score RRF cumulé
        Map<Long, Double> rrfScores = new HashMap<>();

        // Pour chaque liste de résultats
        for (List<Long> rankedList : rankedLists) {
            // Pour chaque item dans la liste
            for (int rank = 0; rank < rankedList.size(); rank++) {
                long nodeId = rankedList.get(rank);
                int position = rank + 1; // Les rangs commencent à 1

                // Calcul du score RRF : 1 / (k + rank)
                double rrfScore = 1.0 / (k + position);

                // Accumulation des scores
                rrfScores.merge(nodeId, rrfScore, Double::sum);
            }
        }

        // Tri par score RRF décroissant et limitation au Top K
        return rrfScores.entrySet().stream()
            .sorted(Map.Entry.<Long, Double>comparingByValue().reversed())
            .limit(topK)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }

    /**
     * Fusionne plusieurs listes avec k = 60 par défaut.
     *
     * @param rankedLists Liste de listes classées
     * @param topK        Nombre de résultats à retourner
     * @return Liste fusionnée des Top K résultats
     */
    public static List<Long> fuse(List<List<Long>> rankedLists, int topK) {
        return fuse(rankedLists, DEFAULT_K, topK);
    }

    /**
     * Calcule le score RRF pour un item donné dans plusieurs listes.
     * Utilisé principalement pour les tests et le débogage.
     *
     * @param nodeId      Identifiant du nœud
     * @param rankedLists Listes classées contenant (ou non) ce nœud
     * @param k           Constante de régularisation
     * @return Score RRF du nœud (somme des contributions de chaque liste)
     */
    public static double calculateScore(long nodeId, List<List<Long>> rankedLists, int k) {
        double score = 0.0;

        for (List<Long> rankedList : rankedLists) {
            int position = rankedList.indexOf(nodeId);
            if (position != -1) {
                int rank = position + 1;
                score += 1.0 / (k + rank);
            }
        }

        return score;
    }

    /**
     * Variante qui retourne à la fois les IDs et leurs scores RRF.
     * Utile pour le débogage et l'analyse des résultats.
     *
     * @param rankedLists Liste de listes classées
     * @param k           Constante de régularisation
     * @param topK        Nombre de résultats à retourner
     * @return Map ordonnée : nodeId → score RRF (Top K)
     */
    public static Map<Long, Double> fuseWithScores(List<List<Long>> rankedLists, int k, int topK) {
        if (rankedLists == null || rankedLists.isEmpty()) {
            throw new IllegalArgumentException("rankedLists ne peut pas être vide");
        }
        if (topK <= 0) {
            throw new IllegalArgumentException("topK doit être > 0");
        }

        Map<Long, Double> rrfScores = new HashMap<>();

        for (List<Long> rankedList : rankedLists) {
            for (int rank = 0; rank < rankedList.size(); rank++) {
                long nodeId = rankedList.get(rank);
                int position = rank + 1;
                double rrfScore = 1.0 / (k + position);
                rrfScores.merge(nodeId, rrfScore, Double::sum);
            }
        }

        return rrfScores.entrySet().stream()
            .sorted(Map.Entry.<Long, Double>comparingByValue().reversed())
            .limit(topK)
            .collect(Collectors.toMap(
                Map.Entry::getKey,
                Map.Entry::getValue,
                (e1, e2) -> e1,
                LinkedHashMap::new
            ));
    }
}
