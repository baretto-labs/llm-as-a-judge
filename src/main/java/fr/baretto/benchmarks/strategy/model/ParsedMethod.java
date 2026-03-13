package fr.baretto.benchmarks.strategy.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Représente une méthode Java.
 */
public class ParsedMethod {
    public String name;
    public String fqn;
    public String returnType; // Nom simple
    public String visibility;
    public boolean isStatic;
    public boolean isAbstract;
    public boolean isFinal;

    // Paramètres
    public List<ParsedParameter> parameters = new ArrayList<>();

    // Annotations
    public List<String> annotations = new ArrayList<>();

    // Appels de méthodes détectés (syntaxe)
    public List<ParsedMethodCall> calls = new ArrayList<>();

    // Variables locales (Phase 1)
    public List<ParsedLocalVariable> localVariables = new ArrayList<>();

    // Scope de variables pour résolution (Phase 1)
    public VariableScope variableScope = new VariableScope();

    // Résolution (rempli en Phase 2)
    public String resolvedReturnType; // FQN résolu

    public ParsedMethod(String name, String fqn) {
        this.name = name;
        this.fqn = fqn;
    }
}
