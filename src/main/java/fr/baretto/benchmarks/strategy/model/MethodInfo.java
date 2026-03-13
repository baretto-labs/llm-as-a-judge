package fr.baretto.benchmarks.strategy.model;

import java.util.List;

/**
 * Informations sur une méthode pour la Symbol Table.
 */
public class MethodInfo {
    public String fqn;
    public String name;
    public List<String> parameterTypes;
    public String returnType;

    public MethodInfo(String fqn, String name) {
        this.fqn = fqn;
        this.name = name;
    }
}
