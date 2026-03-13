package fr.baretto.benchmarks.search;

import java.util.Map;

/**
 * Représente un point d'entrée dans le graphe de code.
 * Résultat d'une recherche hybride (lexicale + vectorielle).
 *
 * @param nodeId     Identifiant unique du nœud Neo4j
 * @param nodeType   Type du nœud (Class, Method, Interface, etc.)
 * @param name       Nom du nœud (ex: "UserService", "findById")
 * @param fqn        Fully Qualified Name (ex: "com.example.UserService")
 * @param score      Score de pertinence final (après fusion RRF)
 * @param properties Propriétés additionnelles du nœud (signature, javaDoc, etc.)
 */
public record EntryPoint(
    long nodeId,
    String nodeType,
    String name,
    String fqn,
    double score,
    Map<String, Object> properties
) implements Comparable<EntryPoint> {

    /**
     * Compare les EntryPoints par score décroissant.
     * Utilisé pour trier les résultats (meilleurs scores en premier).
     */
    @Override
    public int compareTo(EntryPoint other) {
        return Double.compare(other.score, this.score); // Ordre décroissant
    }

    /**
     * Constructeur simplifié sans propriétés additionnelles.
     */
    public EntryPoint(long nodeId, String nodeType, String name, String fqn, double score) {
        this(nodeId, nodeType, name, fqn, score, Map.of());
    }

    @Override
    public String toString() {
        return String.format("%s:%s (score=%.4f, fqn=%s)", nodeType, name, score, fqn);
    }
}
