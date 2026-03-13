package fr.baretto.benchmarks.strategy.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Représente une classe, interface, enum, record ou annotation Java.
 */
public class ParsedClass {
    public String name;
    public String fqn;
    public String type; // "class", "interface", "enum", "record", "@interface"
    public String visibility; // "public", "private", "protected", "package-private"
    public List<String> modifiers = new ArrayList<>(); // "abstract", "final", "static", etc.

    // Héritage
    public List<String> extendsTypes = new ArrayList<>(); // Noms simples
    public List<String> implementsTypes = new ArrayList<>(); // Noms simples

    // Résolution (rempli en Phase 2)
    public List<String> resolvedExtends = new ArrayList<>(); // FQN résolus
    public List<String> resolvedImplements = new ArrayList<>(); // FQN résolus

    // Membres
    public List<ParsedMethod> methods = new ArrayList<>();
    public List<ParsedConstructor> constructors = new ArrayList<>();
    public List<ParsedField> fields = new ArrayList<>();
    public List<String> annotations = new ArrayList<>();

    // Contexte du fichier pour résolution
    public List<String> fileImports = new ArrayList<>();  // FQNs des imports
    public String packageName;                             // Package du fichier

    public ParsedClass(String name, String fqn, String type) {
        this.name = name;
        this.fqn = fqn;
        this.type = type;
    }
}
