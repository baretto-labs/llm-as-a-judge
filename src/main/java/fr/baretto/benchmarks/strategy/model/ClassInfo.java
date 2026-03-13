package fr.baretto.benchmarks.strategy.model;

import java.util.HashMap;
import java.util.Map;

/**
 * Informations sur une classe pour la Symbol Table.
 */
public class ClassInfo {
    public String fqn;
    public String simpleName;
    public String packageName;
    public String filePath;
    public Map<String, MethodInfo> methods = new HashMap<>();

    public ClassInfo(String fqn, String simpleName, String packageName) {
        this.fqn = fqn;
        this.simpleName = simpleName;
        this.packageName = packageName;
    }

    /**
     * Récupère une méthode par nom (sans surcharge pour l'instant).
     */
    public MethodInfo getMethod(String methodName) {
        return methods.get(methodName);
    }

    /**
     * Ajoute une méthode à la table.
     */
    public void addMethod(MethodInfo methodInfo) {
        methods.put(methodInfo.name, methodInfo);
    }
}
