package fr.baretto.benchmarks.strategy.model;

import java.util.HashMap;
import java.util.Map;

/**
 * Scope de variables pour une méthode (paramètres + variables locales).
 * Permet de résoudre les types des variables pour la résolution des appels de méthodes.
 */
public class VariableScope {
    private Map<String, String> variables = new HashMap<>(); // name → FQN type

    /**
     * Ajoute une variable au scope avec son type résolu.
     * @param name Nom de la variable
     * @param resolvedType Type FQN résolu (ex: "com.example.User")
     */
    public void addVariable(String name, String resolvedType) {
        variables.put(name, resolvedType);
    }

    /**
     * Récupère le type résolu d'une variable.
     * @param variableName Nom de la variable
     * @return Type FQN ou null si non trouvé
     */
    public String getVariableType(String variableName) {
        return variables.get(variableName);
    }

    /**
     * Vérifie si une variable existe dans le scope.
     * @param variableName Nom de la variable
     * @return true si la variable existe
     */
    public boolean hasVariable(String variableName) {
        return variables.containsKey(variableName);
    }
}
