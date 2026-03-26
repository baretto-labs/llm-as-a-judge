package fr.baretto.benchmarks.jmh;

import fr.baretto.benchmarks.strategy.FeatureFlags;
import fr.baretto.benchmarks.strategy.LuceneRagStrategy;
import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;

import java.io.IOException;
import java.util.Locale;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

/**
 * Microbenchmark JMH — temps de retrieval par taille de projet indexé.
 *
 * L'indexation est faite une seule fois en @Setup(Trial) pour chaque taille.
 * On mesure ensuite uniquement le retrieval (embedding query + search).
 *
 * Neo4j utilise Hybrid Search (BM25 + KNN + RRF + K-hop) sans LLM reranker.
 * Lucene utilise BM25 + KNN + RRF (top-10, même pipeline de base que Neo4j sans le graphe).
 *
 * <p>Le juge LLM est exécuté dans {@code @TearDown(Invocation)}, hors fenêtre de mesure,
 * pour ne pas contaminer les temps de retrieval avec l'inférence ≥14B.
 * Désactivable via {@code -Djmh.judge.enabled=false}.</p>
 *
 * <p>Sorties :</p>
 * <ul>
 *   <li>{@code target/jmh-judge.jsonl} — synthèse par (strategy, scenario, fileCount, difficulty)</li>
 *   <li>{@code target/jmh-judge-detail.jsonl} — une ligne par question avec contexte généré et score</li>
 * </ul>
 */
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
@State(Scope.Benchmark)
@Threads(1)  // pending* et les listes de résultats sont partagés non thread-safe
@Fork(1)
@Warmup(iterations = 3, time = 1)
@Measurement(iterations = 5, time = 1)
public class RetrievalBenchmark {

    @Param({"10", "100", "1000", "10000"})
    public int fileCount;

    /**
     * Scénario de comparaison encodé {@code "preset-lucene|preset-neo4j"}.
     *
     * <ul>
     *   <li>{@code knn-only|hybrid}           — valeur du BM25+RRF (indépendant du graphe)</li>
     *   <li>{@code hybrid|hybrid}             — fairness check : même pipeline de base</li>
     *   <li>{@code hybrid|hybrid-graph}       — valeur marginale de l'expansion K-hop</li>
     *   <li>{@code hybrid|hybrid-graph-hyde}  — valeur marginale de HyDE</li>
     * </ul>
     *
     * Utiliser {@code -p scenario=hybrid|hybrid-graph} pour cibler un seul scénario.
     */
    @Param({"knn-only|hybrid", "hybrid|hybrid", "hybrid|hybrid-graph", "hybrid|hybrid-graph-hyde"})
    public String scenario;

    private LuceneRagStrategy     luceneStrategy;
    private Neo4jGraphRagStrategy neo4jStrategy;
    private Path                  luceneDir;
    private Path                  neo4jDir;
    private Path                  sourceDir;
    private boolean               syntheticSource = true;

    /** Corpus complet (toutes difficultés). Peut être filtré via -Djmh.difficulty=LOCAL|STRUCTURAL|CROSS_MODULE */
    private List<QuestionCorpus.Question> questions;
    private int queryIdx;

    // Juge LLM
    private LLMJudge llmJudge;
    private String   judgeModelName;

    /**
     * Résultat complet d'une invocation jugée : question posée, contexte retourné, verdict.
     * Stocké hors fenêtre de mesure pour écriture en fin de trial.
     */
    private record TrialResult(
        QuestionCorpus.Question  question,
        List<String>             context,
        LLMJudge.JudgementResult judgement
    ) {}

    /** Paire (question, contexte) collectée pendant la mesure, jugée en batch dans teardownTrial. */
    private record PendingJudgement(QuestionCorpus.Question question, List<String> context) {}

    private final List<TrialResult>    luceneTrialResults      = new java.util.ArrayList<>();
    private final List<TrialResult>    neo4jTrialResults       = new java.util.ArrayList<>();
    private final List<PendingJudgement> pendingLuceneJudgements = new java.util.ArrayList<>();
    private final List<PendingJudgement> pendingNeo4jJudgements  = new java.util.ArrayList<>();

    // Résultats en attente — écrits dans @Benchmark, collectés dans @TearDown(Invocation)
    private QuestionCorpus.Question pendingJudgeQuestion;
    private List<String>            pendingLuceneResult;
    private List<String>            pendingNeo4jResult;

    // ── Setup ───────────────────────────────────────────────────────────────

    /**
     * Indexation faite une seule fois par (benchmark × fileCount).
     * Neo4j démarre et indexe ici — coût non mesuré dans les itérations.
     *
     * <p>Si la propriété système {@code rag.source.dir} est définie, le benchmark
     * utilise ce répertoire réel au lieu de générer un corpus synthétique.
     * Dans ce cas, le paramètre {@code fileCount} est ignoré.</p>
     *
     * <pre>
     *   -Drag.source.dir=/path/to/real/project/src/main/java
     * </pre>
     */
    @Setup(Level.Trial)
    public void setupTrial() throws Exception {
        // Env var takes priority (inherited by JMH fork), system property as fallback
        String realSourceDir = System.getenv("RAG_SOURCE_DIR");
        if (realSourceDir == null) realSourceDir = System.getProperty("rag.source.dir");
        if (realSourceDir != null) {
            sourceDir = Path.of(realSourceDir);
            syntheticSource = false;
        } else {
            sourceDir = BenchmarkSources.create(fileCount);
            syntheticSource = true;
        }

        String[] parts = scenario.split("\\|", 2);
        FeatureFlags luceneFlags = FeatureFlags.fromPreset(parts[0]);
        FeatureFlags neo4jFlags  = FeatureFlags.fromPreset(parts.length > 1 ? parts[1] : parts[0]);

        luceneDir = Files.createTempDirectory("bench-lucene-ret-" + fileCount);
        luceneStrategy = new LuceneRagStrategy(luceneDir, luceneFlags);
        luceneStrategy.indexDirectory(sourceDir);

        neo4jDir = Files.createTempDirectory("bench-neo4j-ret-" + fileCount);
        neo4jStrategy = new Neo4jGraphRagStrategy(neo4jDir.toString(), neo4jFlags);
        neo4jStrategy.indexDirectory(sourceDir);

        String diffFilter = System.getProperty("jmh.difficulty");
        questions = diffFilter == null
            ? QuestionCorpus.QUESTIONS
            : QuestionCorpus.QUESTIONS.stream()
                .filter(q -> q.difficulty().name().equalsIgnoreCase(diffFilter))
                .toList();

        boolean judgeEnabled = !"false".equalsIgnoreCase(System.getProperty("jmh.judge.enabled", "true"));
        llmJudge = judgeEnabled ? new LLMJudge() : null;
        judgeModelName = llmJudge != null ? llmJudge.getModelNamesLabel() : "disabled";
        queryIdx = 0;
        luceneTrialResults.clear();
        neo4jTrialResults.clear();
        pendingLuceneJudgements.clear();
        pendingNeo4jJudgements.clear();
    }

    @TearDown(Level.Trial)
    public void teardownTrial() throws Exception {
        runBatchJudgements();
        printJudgeSummary();
        luceneStrategy.close();
        neo4jStrategy.close();
        deleteDir(luceneDir);
        deleteDir(neo4jDir);
        if (syntheticSource) {
            BenchmarkSources.delete(sourceDir);
        }
    }

    @Setup(Level.Invocation)
    public void rotateQuery() {
        queryIdx = (queryIdx + 1) % questions.size();
    }

    // ── Benchmarks ──────────────────────────────────────────────────────────

    @Benchmark
    public void luceneRetrieval(MemoryStats mem, CpuStats cpu, ContextStats ctx, Blackhole bh) throws Exception {
        QuestionCorpus.Question q = questions.get(queryIdx);
        List<String> result = luceneStrategy.retrieveContext(q.text());
        ctx.recordContext(result);
        pendingJudgeQuestion = q;
        pendingLuceneResult  = result;
        pendingNeo4jResult   = null;
        bh.consume(result);
    }

    @Benchmark
    public void neo4jRetrieval(MemoryStats mem, CpuStats cpu, ContextStats ctx, Blackhole bh) throws Exception {
        QuestionCorpus.Question q = questions.get(queryIdx);
        List<String> result = neo4jStrategy.retrieveContext(q.text());
        ctx.recordContext(result);
        pendingJudgeQuestion = q;
        pendingNeo4jResult   = result;
        pendingLuceneResult  = null;
        bh.consume(result);
    }

    /**
     * Collecte (question, contexte) après chaque invocation SANS appeler le juge.
     * Le jugement en batch est fait dans {@link #runBatchJudgements()} appelé depuis teardownTrial,
     * pour ne pas bloquer la boucle de mesure JMH avec la latence du LLM (~14s/appel).
     */
    @TearDown(Level.Invocation)
    public void judgeInvocation() {
        if (llmJudge == null || pendingJudgeQuestion == null) return;
        QuestionCorpus.Question q = pendingJudgeQuestion;
        List<String> lr = pendingLuceneResult;
        if (lr != null) {
            pendingLuceneJudgements.add(new PendingJudgement(q, lr));
            pendingLuceneResult = null;
        }
        List<String> nr = pendingNeo4jResult;
        if (nr != null) {
            pendingNeo4jJudgements.add(new PendingJudgement(q, nr));
            pendingNeo4jResult = null;
        }
        pendingJudgeQuestion = null;
    }

    /**
     * Appelle le juge en batch sur une invocation par question unique.
     * Déduplique pour éviter de juger N fois la même question — on garde la dernière occurrence.
     */
    private void runBatchJudgements() {
        if (llmJudge == null) return;
        List<PendingJudgement> luceneDedup = dedupByQuestion(pendingLuceneJudgements);
        List<PendingJudgement> neo4jDedup  = dedupByQuestion(pendingNeo4jJudgements);
        System.out.printf("[Judge] Batch judging %d Lucene + %d Neo4j unique questions...%n",
            luceneDedup.size(), neo4jDedup.size());
        for (PendingJudgement p : luceneDedup) {
            luceneTrialResults.add(new TrialResult(p.question(), p.context(),
                llmJudge.judge(p.question().text(), p.context(), p.question().expectedFqnHints())));
        }
        for (PendingJudgement p : neo4jDedup) {
            neo4jTrialResults.add(new TrialResult(p.question(), p.context(),
                llmJudge.judge(p.question().text(), p.context(), p.question().expectedFqnHints())));
        }
    }

    /** Garde la dernière invocation par question unique (texte exact). */
    private List<PendingJudgement> dedupByQuestion(List<PendingJudgement> list) {
        var seen = new java.util.LinkedHashMap<String, PendingJudgement>();
        for (PendingJudgement p : list) seen.put(p.question().text(), p);
        return new java.util.ArrayList<>(seen.values());
    }

    // ── AuxCounters ─────────────────────────────────────────────────────────

    @State(Scope.Thread)
    @AuxCounters(AuxCounters.Type.EVENTS)
    public static class MemoryStats {
        public long heapDeltaMB;
        private long before;

        @Setup(Level.Invocation)
        public void before() { System.gc(); before = usedHeap(); }

        @TearDown(Level.Invocation)
        public void after() { heapDeltaMB = Math.max(0, (usedHeap() - before) / (1024 * 1024)); }

        private long usedHeap() { return Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory(); }
    }

    @State(Scope.Thread)
    @AuxCounters(AuxCounters.Type.EVENTS)
    public static class CpuStats {
        public long cpuTimeMs;
        private long before;

        @Setup(Level.Invocation)
        public void before() { before = ManagementFactory.getThreadMXBean().getCurrentThreadCpuTime(); }

        @TearDown(Level.Invocation)
        public void after() { cpuTimeMs = Math.max(0, (ManagementFactory.getThreadMXBean().getCurrentThreadCpuTime() - before) / 1_000_000); }
    }

    @State(Scope.Thread)
    @AuxCounters(AuxCounters.Type.EVENTS)
    public static class ContextStats {
        public long contextTokensEstimate;
        public long emptyContextCount;

        void recordContext(List<String> context) {
            int totalChars = context.stream().mapToInt(String::length).sum();
            contextTokensEstimate = totalChars / 4;
            emptyContextCount = (totalChars < 100) ? 1 : 0;
        }
    }

    // ── Résumé juge ─────────────────────────────────────────────────────────

    private void printJudgeSummary() {
        if (llmJudge == null) {
            System.out.println("[Judge] Désactivé (jmh.judge.enabled=false)");
            return;
        }
        printStrategyJudge("Lucene", luceneTrialResults);
        printStrategyJudge("Neo4j",  neo4jTrialResults);
        writeJudgeResults();
        writeJudgeDetailResults();
    }

    private void printStrategyJudge(String label, List<TrialResult> results) {
        if (results.isEmpty()) return;
        List<LLMJudge.JudgementResult> valid = results.stream()
            .map(TrialResult::judgement)
            .filter(r -> r.score() >= 0).toList();
        if (valid.isEmpty()) { System.out.printf("[Judge] %s: no valid judgements%n", label); return; }

        double avgScore    = valid.stream().mapToInt(LLMJudge.JudgementResult::score).average().orElse(0);
        double avgCoverage = valid.stream().mapToDouble(LLMJudge.JudgementResult::hintCoverage).average().orElse(0);
        long unknownCount  = valid.stream().filter(LLMJudge.JudgementResult::suggestsUnknown).count();

        System.out.printf("[Judge] %s — avg_score=%.2f/10  hint_coverage=%.1f%%  unknown_rate=%.1f%%%n",
            label, avgScore, avgCoverage * 100, (double) unknownCount / valid.size() * 100);
    }

    /**
     * Écrit {@code target/jmh-judge.jsonl} — synthèse par trial.
     * Une ligne difficulty=ALL (agrégée) + une ligne par niveau de difficulté.
     */
    private void writeJudgeResults() {
        try {
            java.nio.file.Path out = java.nio.file.Path.of("target/jmh-judge.jsonl");
            java.nio.file.Files.createDirectories(out.getParent());
            StringBuilder sb = new StringBuilder();
            for (String strat : new String[]{"lucene", "neo4j"}) {
                List<TrialResult> res = strat.equals("lucene") ? luceneTrialResults : neo4jTrialResults;
                appendJudgeLine(sb, res, strat, "ALL");
                for (QuestionCorpus.Difficulty diff : QuestionCorpus.Difficulty.values()) {
                    List<TrialResult> sub = res.stream()
                        .filter(tr -> tr.question().difficulty() == diff).toList();
                    appendJudgeLine(sb, sub, strat, diff.name());
                }
            }
            java.nio.file.Files.writeString(out, sb.toString(),
                java.nio.file.StandardOpenOption.CREATE,
                java.nio.file.StandardOpenOption.APPEND);
        } catch (Exception e) {
            System.err.println("[Judge] Impossible d'écrire jmh-judge.jsonl: " + e.getMessage());
        }
    }

    private void appendJudgeLine(StringBuilder sb, List<TrialResult> results, String strategy, String difficulty) {
        List<LLMJudge.JudgementResult> valid = results.stream()
            .map(TrialResult::judgement)
            .filter(r -> r.score() >= 0).toList();
        if (valid.isEmpty()) return;
        double avgScore    = valid.stream().mapToInt(LLMJudge.JudgementResult::score).average().orElse(-1);
        double avgCoverage = valid.stream().mapToDouble(LLMJudge.JudgementResult::hintCoverage).average().orElse(-1);
        double unknownRate = (double) valid.stream().filter(LLMJudge.JudgementResult::suggestsUnknown).count() / valid.size();
        sb.append(String.format(Locale.ROOT,
            "{\"ts\":\"%s\",\"strategy\":\"%s\",\"scenario\":\"%s\",\"fileCount\":%d," +
            "\"difficulty\":\"%s\",\"avgScore\":%.2f,\"avgHintCoverage\":%.3f,\"unknownRate\":%.3f," +
            "\"n\":%d,\"judgeModel\":\"%s\"}%n",
            java.time.Instant.now(), strategy, scenario, fileCount,
            difficulty, avgScore, avgCoverage, unknownRate, valid.size(), judgeModelName));
    }

    /**
     * Écrit {@code target/jmh-judge-detail.jsonl} — une ligne par question jugée.
     * Contient : question, difficulté, attendu (expectedFqnHints), généré (contexte retourné), score, rationale.
     * Utilisé par le dashboard pour l'affichage "généré vs attendu vs note".
     */
    private void writeJudgeDetailResults() {
        try {
            java.nio.file.Path out = java.nio.file.Path.of("target/jmh-judge-detail.jsonl");
            java.nio.file.Files.createDirectories(out.getParent());
            StringBuilder sb = new StringBuilder();
            appendDetailLines(sb, luceneTrialResults, "lucene");
            appendDetailLines(sb, neo4jTrialResults,  "neo4j");
            java.nio.file.Files.writeString(out, sb.toString(),
                java.nio.file.StandardOpenOption.CREATE,
                java.nio.file.StandardOpenOption.APPEND);
        } catch (Exception e) {
            System.err.println("[Judge] Impossible d'écrire jmh-judge-detail.jsonl: " + e.getMessage());
        }
    }

    private void appendDetailLines(StringBuilder sb, List<TrialResult> results, String strategy) {
        for (TrialResult tr : results) {
            if (tr.judgement().score() < 0) continue;
            String generatedCtx = String.join("\n---\n", tr.context());
            if (generatedCtx.length() > 3000) {
                generatedCtx = generatedCtx.substring(0, 3000) + "\n[...]";
            }
            String expectedJson = Arrays.stream(tr.question().expectedFqnHints())
                .map(h -> "\"" + jsonEscape(h) + "\"")
                .collect(Collectors.joining(",", "[", "]"));
            sb.append(String.format(Locale.ROOT,
                "{\"ts\":\"%s\",\"strategy\":\"%s\",\"scenario\":\"%s\",\"fileCount\":%d," +
                "\"question\":\"%s\",\"difficulty\":\"%s\",\"expected\":%s," +
                "\"generated\":\"%s\",\"score\":%d,\"rationale\":\"%s\"," +
                "\"hintCoverage\":%.3f,\"suggestsUnknown\":%b,\"judgeModel\":\"%s\"}%n",
                java.time.Instant.now(), strategy, scenario, fileCount,
                jsonEscape(tr.question().text()),
                tr.question().difficulty().name(),
                expectedJson,
                jsonEscape(generatedCtx),
                tr.judgement().score(),
                jsonEscape(tr.judgement().rationale()),
                tr.judgement().hintCoverage(),
                tr.judgement().suggestsUnknown(),
                judgeModelName));
        }
    }

    private static String jsonEscape(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    // ── Utilitaire ──────────────────────────────────────────────────────────

    private void deleteDir(Path dir) throws IOException {
        if (dir != null && Files.exists(dir)) {
            Files.walk(dir).sorted(Comparator.reverseOrder())
                    .forEach(p -> { try { Files.delete(p); } catch (IOException ignored) {} });
        }
    }
}
