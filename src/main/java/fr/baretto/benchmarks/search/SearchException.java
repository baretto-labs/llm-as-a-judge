package fr.baretto.benchmarks.search;

/**
 * Exception levée lors d'une erreur de recherche dans le graphe.
 * Peut être causée par :
 * <ul>
 *   <li>Base de données Neo4j inaccessible</li>
 *   <li>Service d'embedding (LLM) indisponible</li>
 *   <li>Index Full-text ou Vectoriel manquant</li>
 *   <li>Requête invalide</li>
 * </ul>
 */
public class SearchException extends Exception {

    public SearchException(String message) {
        super(message);
    }

    public SearchException(String message, Throwable cause) {
        super(message, cause);
    }

    public SearchException(Throwable cause) {
        super(cause);
    }
}
