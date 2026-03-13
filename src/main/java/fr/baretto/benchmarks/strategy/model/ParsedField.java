package fr.baretto.benchmarks.strategy.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Représente un field/propriété Java.
 */
public class ParsedField {
    public String name;
    public String fqn;
    public String type; // Nom simple
    public String visibility;
    public boolean isStatic;
    public boolean isFinal;

    public List<String> annotations = new ArrayList<>();

    // Résolution (rempli en Phase 2)
    public String resolvedType; // FQN résolu

    public ParsedField(String name, String fqn, String type) {
        this.name = name;
        this.fqn = fqn;
        this.type = type;
    }
}
