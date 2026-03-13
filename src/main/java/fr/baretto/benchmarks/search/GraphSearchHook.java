package fr.baretto.benchmarks.search;

import java.util.List;

/**
 * Hook de recherche dans le graphe de code.
 * Permet de trouver les meilleurs points d'entrée (Classes, Méthodes)
 * pour répondre à une question utilisateur.
 *
 * <p>Les implémentations peuvent utiliser différentes stratégies :
 * <ul>
 *   <li>Recherche lexicale (Full-text, BM25)</li>
 *   <li>Recherche vectorielle (embeddings + cosine similarity)</li>
 *   <li>Recherche hybride (fusion des deux approches)</li>
 * </ul>
 */
public interface GraphSearchHook {

    /**
     * Trouve les meilleurs points d'entrée dans le graphe pour une requête donnée.
     *
     * @param query Question ou requête utilisateur (ex: "Comment créer un utilisateur ?")
     * @param topK  Nombre de résultats à retourner (ex: 3 pour Top 3)
     * @return Liste ordonnée des meilleurs points d'entrée (score décroissant)
     * @throws SearchException Si la recherche échoue (base inaccessible, embeddings indisponibles, etc.)
     */
    List<EntryPoint> findEntryPoints(String query, int topK) throws SearchException;

    /**
     * Trouve les meilleurs points d'entrée avec topK = 3 par défaut.
     *
     * @param query Question ou requête utilisateur
     * @return Top 3 des meilleurs points d'entrée
     * @throws SearchException Si la recherche échoue
     */
    default List<EntryPoint> findEntryPoints(String query) throws SearchException {
        return findEntryPoints(query, 3);
    }
}
