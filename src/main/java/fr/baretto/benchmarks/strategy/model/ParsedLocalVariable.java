package fr.baretto.benchmarks.strategy.model;

/**
 * Représente une variable locale déclarée dans une méthode.
 * Utilisé pour le tracking des types et la résolution des appels de méthodes.
 */
public class ParsedLocalVariable {
    public String name;           // Nom de la variable
    public String type;           // Type simple (ex: "User")
    public String resolvedType;   // FQN résolu (ex: "com.example.User")
    public int declarationLine;   // Ligne de déclaration (pour debug)

    public ParsedLocalVariable(String name, String type) {
        this.name = name;
        this.type = type;
    }
}
