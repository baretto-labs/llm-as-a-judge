package fr.baretto.benchmarks.strategy;

import java.nio.file.Path;
import java.util.List;

/**
 * Interface définissant le contrat pour les stratégies RAG (Retrieval-Augmented Generation).
 * Permet de définir différentes implémentations (Vectoriel, GraphRAG).
 */
public interface RagStrategy {

    /**
     * Indexe le contenu d'un répertoire (codebase) pour la recherche.
     *
     * @param directoryPath le chemin du répertoire à indexer
     * @throws Exception si une erreur survient pendant l'indexation
     */
    void indexDirectory(Path directoryPath) throws Exception;

    /**
     * Récupère le contexte pertinent pour une requête donnée.
     *
     * @param query la requête de l'utilisateur
     * @return une liste de fragments de texte pertinents
     * @throws Exception si une erreur survient pendant la recherche
     */
    List<String> retrieveContext(String query) throws Exception;

    /**
     * Retourne le nom de la stratégie (pour affichage).
     *
     * @return le nom de la stratégie
     */
    String getStrategyName();

    /**
     * Ferme les ressources utilisées par la stratégie.
     *
     * @throws Exception si une erreur survient pendant la fermeture
     */
    void close() throws Exception;
}
