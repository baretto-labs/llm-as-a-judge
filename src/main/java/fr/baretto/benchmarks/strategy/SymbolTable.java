package fr.baretto.benchmarks.strategy;

import fr.baretto.benchmarks.strategy.model.ClassInfo;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Table de symboles pour résoudre les types et méthodes.
 */
public class SymbolTable {
    // FQN → ClassInfo
    private Map<String, ClassInfo> classByFqn = new HashMap<>();

    // SimpleName → List<ClassInfo> (pour résolution)
    private Map<String, List<ClassInfo>> classBySimpleName = new HashMap<>();

    // Package → List<ClassInfo>
    private Map<String, List<ClassInfo>> classByPackage = new HashMap<>();

    /**
     * Ajoute une classe à la table de symboles.
     */
    public void addClass(ClassInfo classInfo) {
        classByFqn.put(classInfo.fqn, classInfo);

        // Index par nom simple
        classBySimpleName.computeIfAbsent(classInfo.simpleName, k -> new ArrayList<>())
                .add(classInfo);

        // Index par package
        if (classInfo.packageName != null && !classInfo.packageName.isEmpty()) {
            classByPackage.computeIfAbsent(classInfo.packageName, k -> new ArrayList<>())
                    .add(classInfo);
        }
    }

    /**
     * Récupère une classe par FQN.
     */
    public ClassInfo getByFqn(String fqn) {
        return classByFqn.get(fqn);
    }

    /**
     * Alias pour getByFqn() - récupère une classe par FQN.
     */
    public ClassInfo getClassByFqn(String fqn) {
        return getByFqn(fqn);
    }

    /**
     * Résout un type à partir de son nom simple.
     * Stratégie de résolution:
     * 1. Chercher dans les imports
     * 2. Chercher dans le même package
     * 3. Chercher dans java.lang
     * 4. Chercher partout (si unique)
     */
    public ClassInfo resolveType(String simpleName, String currentPackage, List<String> imports) {
        // 1. Chercher dans les imports
        for (String imp : imports) {
            if (imp.endsWith("." + simpleName)) {
                ClassInfo resolved = classByFqn.get(imp);
                if (resolved != null) {
                    return resolved;
                }
            }
        }

        // 2. Chercher dans le même package
        ClassInfo inPackage = findInPackage(simpleName, currentPackage);
        if (inPackage != null) {
            return inPackage;
        }

        // 3. Chercher dans java.lang
        ClassInfo javaLang = classByFqn.get("java.lang." + simpleName);
        if (javaLang != null) {
            return javaLang;
        }

        // 4. Chercher partout (si unique)
        List<ClassInfo> candidates = classBySimpleName.get(simpleName);
        if (candidates != null && candidates.size() == 1) {
            return candidates.get(0);
        }

        // Non résolu ou ambigu
        return null;
    }

    /**
     * Cherche une classe dans un package donné.
     */
    private ClassInfo findInPackage(String simpleName, String packageName) {
        List<ClassInfo> classesInPackage = classByPackage.get(packageName);
        if (classesInPackage == null) {
            return null;
        }

        for (ClassInfo classInfo : classesInPackage) {
            if (classInfo.simpleName.equals(simpleName)) {
                return classInfo;
            }
        }

        return null;
    }

    /**
     * Retourne le nombre de classes dans la table.
     */
    public int size() {
        return classByFqn.size();
    }
}
