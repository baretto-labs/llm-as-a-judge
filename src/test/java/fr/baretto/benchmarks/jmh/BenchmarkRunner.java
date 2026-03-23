package fr.baretto.benchmarks.jmh;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.openjdk.jmh.results.format.ResultFormatType;
import org.openjdk.jmh.runner.Runner;
import org.openjdk.jmh.runner.options.ChainedOptionsBuilder;
import org.openjdk.jmh.runner.options.Options;
import org.openjdk.jmh.runner.options.OptionsBuilder;

/**
 * Point d'entrée JUnit 5 pour exécuter les microbenchmarks JMH.
 *
 * <p>Propriétés système supportées :</p>
 * <pre>
 *   -Djmh.include=&lt;regex&gt;            filtre les benchmarks à exécuter
 *   -Djmh.result=&lt;path&gt;              chemin du fichier résultat JSON
 *   -Djmh.params=p1=v1,v2;p2=v3      override des @Param (séparateur ';' entre params)
 *   -Djmh.judge.enabled=false         désactive le juge LLM
 *   -Djmh.judge.model=qwen2.5:14b     modèle juge (défaut : qwen2.5:14b)
 *   -Drag.source.dir=/path/to/src     utilise une vraie codebase au lieu de sources synthétiques
 *   -Djmh.difficulty=LOCAL|STRUCTURAL|CROSS_MODULE  filtre les questions par difficulté
 * </pre>
 *
 * <p>Exemples :</p>
 * <pre>
 *   # Retrieval — tous scénarios, tailles 10 et 100
 *   mvn test -Dtest=BenchmarkRunner#retrieval \
 *     -Djmh.params="scenario=hybrid|hybrid-graph,hybrid|hybrid;fileCount=10,100"
 *
 *   # Retrieval sur vraie codebase
 *   mvn test -Dtest=BenchmarkRunner#retrieval \
 *     -Djmh.params="scenario=knn-only|hybrid,hybrid|hybrid,hybrid|hybrid-graph;fileCount=1" \
 *     -Drag.source.dir=/path/to/project/src/main/java
 *
 *   # Indexation — Lucene uniquement
 *   mvn test -Dtest=BenchmarkRunner#indexation \
 *     -Djmh.include=luceneIndexation -Djmh.params="fileCount=10,100"
 * </pre>
 *
 * <p>Résultats : {@code target/jmh-indexation.json} / {@code target/jmh-retrieval.json}</p>
 */
@Tag("benchmark")
class BenchmarkRunner {

    @Test
    void indexation() throws Exception {
        String result = System.getProperty("jmh.result", "target/jmh-indexation.json");
        ChainedOptionsBuilder builder = new OptionsBuilder()
                .include(resolveInclude(IndexationBenchmark.class.getSimpleName()))
                .resultFormat(ResultFormatType.JSON)
                .result(result);
        applyParams(builder);
        new Runner(builder.build()).run();
    }

    @Test
    void retrieval() throws Exception {
        String result = System.getProperty("jmh.result", "target/jmh-retrieval.json");
        ChainedOptionsBuilder builder = new OptionsBuilder()
                .include(resolveInclude(RetrievalBenchmark.class.getSimpleName()))
                .resultFormat(ResultFormatType.JSON)
                .result(result);
        applyParams(builder);
        applyJvmProps(builder, "rag.source.dir", "jmh.judge.enabled",
                "jmh.judge.model", "jmh.judge.models", "jmh.difficulty");
        new Runner(builder.build()).run();
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private String resolveInclude(String defaultClass) {
        return System.getProperty("jmh.include", defaultClass);
    }

    /**
     * Propage les propriétés système listées vers le JVM forké par JMH.
     * Nécessaire car {@code @Fork(1)} démarre un nouveau processus qui n'hérite
     * pas des {@code -D} passés à Maven.
     */
    private void applyJvmProps(ChainedOptionsBuilder builder, String... keys) {
        for (String key : keys) {
            String val = System.getProperty(key);
            if (val != null) {
                builder.jvmArgsAppend("-D" + key + "=" + val);
            }
        }
    }

    /**
     * Parse {@code -Djmh.params="scenario=v1,v2;fileCount=10,100"} et applique
     * chaque paramètre à l'OptionsBuilder.
     * Séparateur entre paramètres : {@code ;} — séparateur entre valeurs : {@code ,}.
     */
    private void applyParams(ChainedOptionsBuilder builder) {
        String raw = System.getProperty("jmh.params", "").trim();
        if (raw.isEmpty()) return;
        for (String kv : raw.split(";")) {
            String[] parts = kv.split("=", 2);
            if (parts.length == 2) {
                String key    = parts[0].trim();
                String[] vals = parts[1].trim().split(",");
                builder.param(key, vals);
            }
        }
    }
}
