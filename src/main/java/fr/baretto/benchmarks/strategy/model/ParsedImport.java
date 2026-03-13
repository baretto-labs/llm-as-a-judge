package fr.baretto.benchmarks.strategy.model;

/**
 * Représente un import Java.
 */
public class ParsedImport {
    public String fqn;
    public boolean isStatic;
    public boolean isWildcard;

    public ParsedImport(String fqn, boolean isStatic, boolean isWildcard) {
        this.fqn = fqn;
        this.isStatic = isStatic;
        this.isWildcard = isWildcard;
    }
}
