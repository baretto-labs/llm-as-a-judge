package fr.baretto.benchmarks.strategy.model;

/**
 * Représente un paramètre de méthode/constructeur.
 */
public class ParsedParameter {
    public String name;
    public String type; // Nom simple
    public int position;
    public boolean isVarArgs;

    // Résolution (rempli en Phase 2)
    public String resolvedType; // FQN résolu

    public ParsedParameter(String name, String type, int position) {
        this.name = name;
        this.type = type;
        this.position = position;
    }
}
