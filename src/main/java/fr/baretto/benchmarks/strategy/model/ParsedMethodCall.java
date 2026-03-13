package fr.baretto.benchmarks.strategy.model;

/**
 * Représente un appel de méthode détecté dans le code.
 */
public class ParsedMethodCall {
    public String receiver; // "user", "this", "UserRepository", null
    public String methodName; // "save", "findAll", etc.

    // Résolution (rempli en Phase 2)
    public String receiverType; // FQN du type du receiver résolu
    public String targetFqn; // FQN complet de la méthode cible

    public ParsedMethodCall(String receiver, String methodName) {
        this.receiver = receiver;
        this.methodName = methodName;
    }
}
