package fr.baretto.benchmarks.strategy.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Représente un constructeur Java.
 */
public class ParsedConstructor {
    public String name; // Nom de la classe
    public String fqn;
    public String visibility;

    public List<ParsedParameter> parameters = new ArrayList<>();
    public List<String> annotations = new ArrayList<>();

    public ParsedConstructor(String name, String fqn) {
        this.name = name;
        this.fqn = fqn;
    }
}
