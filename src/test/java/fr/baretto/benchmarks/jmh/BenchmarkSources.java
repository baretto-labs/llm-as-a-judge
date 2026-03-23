package fr.baretto.benchmarks.jmh;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;

/**
 * Génère N fichiers Java synthétiques pour les benchmarks.
 *
 * Chaque fichier contient une classe réaliste avec :
 *   - un package (5 packages tournants)
 *   - 4 méthodes dont une qui appelle une autre classe (relation CALLS pour Neo4j)
 *   - des champs, du javadoc, de l'héritage occasionnel
 */
public class BenchmarkSources {

    private static final String[] PACKAGES = {
        "com.example.service",
        "com.example.repository",
        "com.example.controller",
        "com.example.handler",
        "com.example.processor"
    };

    private static final String[] SUFFIXES = {
        "Service", "Repository", "Controller", "Handler", "Processor",
        "Manager", "Factory", "Builder", "Validator", "Converter"
    };

    private static final String[] VERBS = {
        "process", "handle", "validate", "convert", "execute",
        "compute", "resolve", "fetch", "save", "delete"
    };

    private BenchmarkSources() {}

    /**
     * Crée un répertoire temporaire avec {@code count} fichiers Java.
     */
    public static Path create(int count) throws IOException {
        Path dir = Files.createTempDirectory("rag-bench-src-" + count);
        for (int i = 0; i < count; i++) {
            Files.writeString(dir.resolve("Class" + i + ".java"), generateClass(i, count));
        }
        return dir;
    }

    public static void delete(Path dir) throws IOException {
        if (dir != null && Files.exists(dir)) {
            Files.walk(dir)
                    .sorted(Comparator.reverseOrder())
                    .forEach(p -> { try { Files.delete(p); } catch (IOException ignored) {} });
        }
    }

    // ── Génération ──────────────────────────────────────────────────────────

    private static String generateClass(int idx, int total) {
        String pkg        = PACKAGES[idx % PACKAGES.length];
        String suffix     = SUFFIXES[idx % SUFFIXES.length];
        String className  = "Class" + idx + suffix;
        String verb       = VERBS[idx % VERBS.length];

        // référence vers la classe précédente (relation CALLS pour Neo4j)
        int prevIdx       = (idx == 0) ? total - 1 : idx - 1;
        String prevClass  = "Class" + prevIdx + SUFFIXES[prevIdx % SUFFIXES.length];
        String prevPkg    = PACKAGES[prevIdx % PACKAGES.length];

        // héritage occasionnel (tous les 7 fichiers)
        String extendsClause = (idx % 7 == 0 && idx > 0)
                ? " extends Class" + (idx - 1) + SUFFIXES[(idx - 1) % SUFFIXES.length]
                : "";

        return """
                package %s;

                import java.util.List;
                import java.util.ArrayList;
                import %s.%s;

                /**
                 * Auto-generated class %s for benchmark purposes.
                 * Handles %s operations in the system.
                 */
                public class %s%s {

                    private final String id;
                    private final List<String> items = new ArrayList<>();
                    private int counter;

                    public %s(String id) {
                        this.id = id;
                        this.counter = 0;
                    }

                    /** Returns the unique identifier of this instance. */
                    public String getId() {
                        return id;
                    }

                    /**
                     * Processes the given input and delegates to the previous handler.
                     *
                     * @param input the input string to process
                     * @return processed result
                     */
                    public String %sInput(String input) {
                        counter++;
                        %s delegate = new %s(id + "-delegate");
                        String delegated = delegate.getId();
                        items.add(input + ":" + delegated);
                        return id + "::" + input + "::" + counter;
                    }

                    /** Validates that the input is non-null and non-empty. */
                    public boolean isValid(String input) {
                        return input != null && !input.isBlank() && counter >= 0;
                    }

                    /** Returns a snapshot of all processed items. */
                    public List<String> getItems() {
                        return List.copyOf(items);
                    }

                    /** Resets the internal counter and clears the items list. */
                    public void reset() {
                        counter = 0;
                        items.clear();
                    }
                }
                """.formatted(
                pkg, prevPkg, prevClass,
                className, verb,
                className, extendsClause,
                className,
                verb,
                prevClass, prevClass
        );
    }
}
