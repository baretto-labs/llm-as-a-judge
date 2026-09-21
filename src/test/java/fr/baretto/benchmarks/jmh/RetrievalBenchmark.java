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
 *   <li>{@code benchmarks/jmh-judge.jsonl} — synthèse par (strategy, scenario, fileCount, difficulty)</li>
 *   <li>{@code benchmarks/jmh-judge-detail.jsonl} — une ligne par question avec contexte et verdict</li>
 * </ul>
 *
 * <p>Écrit sous {@code benchmarks/} et non {@code target/}, qui est un répertoire de build ignoré
 * par git : ces résultats doivent être versionnés pour que le dépôt serve à reproduire.</p>
 *
 * <ul>
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

    // Juge LLM — verdict binaire depuis le 2026-09-21. L'ancien juge gradué
    // (LLMJudge, échelle 0-10) est déprécié et n'est plus câblé ici.
    private RagContextJudge judge;
    private String          judgeModelName;

    /**
     * Résultat complet d'une invocation jugée : question posée, contexte retourné, verdict.
     * Stocké hors fenêtre de mesure pour écriture en fin de trial.
     */
    private record TrialResult(
        QuestionCorpus.Question    question,
        List<String>               context,
        RagContextJudge.Judgement  judgement
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
        // Une propriété non renseignée arrive comme chaîne vide depuis surefire : la traiter
        // comme absente, sinon Path.of("") indexerait le répertoire courant.
        String realSourceDir = System.getenv("RAG_SOURCE_DIR");
        if (realSourceDir == null || realSourceDir.isBlank()) realSourceDir = System.getProperty("rag.source.dir");
        if (realSourceDir != null && !realSourceDir.isBlank()) {
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

        // Désactivé par défaut depuis le 2026-09-21 : juger dans le cycle de vie de JMH produisait
        // deux défauts — l'échéance de 10 min par itération interrompait le jugement à mi-parcours
        // (70 INVALID sur 120), et chaque @Benchmark étant son propre essai, Lucene et Neo4j ne
        // coexistaient jamais, rendant le test apparié impossible. La qualité se mesure désormais
        // dans RagQualityEvaluation ; ce banc-ci ne mesure plus que des latences.
        boolean judgeEnabled = "true".equalsIgnoreCase(System.getProperty("jmh.judge.enabled", "false"));
        judge = judgeEnabled ? new RagContextJudge() : null;
        judgeModelName = judge != null ? judge.getModelLabel() : "disabled";
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
        if (judge == null || pendingJudgeQuestion == null) return;
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
        if (judge == null) return;
        List<PendingJudgement> luceneDedup = dedupByQuestion(pendingLuceneJudgements);
        List<PendingJudgement> neo4jDedup  = dedupByQuestion(pendingNeo4jJudgements);
        System.out.printf("[Judge] Batch judging %d Lucene + %d Neo4j unique questions...%n",
            luceneDedup.size(), neo4jDedup.size());
        for (PendingJudgement p : luceneDedup) {
            luceneTrialResults.add(new TrialResult(p.question(), p.context(),
                judge.judge(p.question().text(), p.context(), p.question().expectedFqnHints())));
        }
        for (PendingJudgement p : neo4jDedup) {
            neo4jTrialResults.add(new TrialResult(p.question(), p.context(),
                judge.judge(p.question().text(), p.context(), p.question().expectedFqnHints())));
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
        if (judge == null) {
            System.out.println("[Judge] Désactivé (jmh.judge.enabled=false)");
            return;
        }
        printStrategyJudge("Lucene", luceneTrialResults);
        printStrategyJudge("Neo4j",  neo4jTrialResults);
        printMcNemar();
        writeJudgeResults();
        writeJudgeDetailResults();
    }

    private void printStrategyJudge(String label, List<TrialResult> results) {
        if (results.isEmpty()) return;
        List<RagContextJudge.Judgement> valid = results.stream()
            .map(TrialResult::judgement)
            .filter(j -> !j.isInvalid()).toList();
        if (valid.isEmpty()) { System.out.printf("[Judge] %s: no valid judgements%n", label); return; }

        double passRate    = (double) valid.stream().filter(RagContextJudge.Judgement::isPass).count() / valid.size();
        double avgCoverage = valid.stream().mapToDouble(RagContextJudge.Judgement::hintCoverage).average().orElse(0);
        double coherence   = (double) valid.stream().filter(RagContextJudge.Judgement::coherent).count() / valid.size();
        long invalides     = results.size() - valid.size();

        System.out.printf("[Judge] %s — pass_rate=%.1f%%  hint_coverage=%.1f%%  coherence=%.1f%%  invalid=%d/%d%n",
            label, passRate * 100, avgCoverage * 100, coherence * 100, invalides, results.size());
    }

    /**
     * Comparaison appariée des deux stratégies sur les questions communes.
     *
     * <p>Les deux répondent aux <b>mêmes</b> questions : le test apparié est donc le bon, et deux
     * taux comparés indépendamment seraient une erreur. Seules les paires <b>discordantes</b>
     * portent de l'information — à cet effectif, leur nombre est le vrai déterminant de la
     * puissance, et il est imprimé avec le p.</p>
     */
    private void printMcNemar() {
        var parQuestion = new java.util.LinkedHashMap<String, Boolean>();
        for (TrialResult tr : luceneTrialResults) {
            if (!tr.judgement().isInvalid()) parQuestion.put(tr.question().text(), tr.judgement().isPass());
        }
        int b = 0, c = 0;
        for (TrialResult tr : neo4jTrialResults) {
            if (tr.judgement().isInvalid()) continue;
            Boolean lucene = parQuestion.get(tr.question().text());
            if (lucene == null) continue;
            boolean neo4j = tr.judgement().isPass();
            if (lucene && !neo4j) b++;
            else if (!lucene && neo4j) c++;
        }
        int n = b + c;
        if (n == 0) {
            System.out.println("[Judge] McNemar : aucune paire discordante, rien à conclure");
            return;
        }
        double queue = 0;
        for (int i = 0; i <= Math.min(b, c); i++) queue += binomiale(n, i);
        double p = Math.min(1.0, 2 * queue / Math.pow(2, n));
        System.out.printf("[Judge] McNemar exact bilatéral : p=%.4f sur %d paires discordantes "
                + "(Lucene seul PASS %d, Neo4j seul PASS %d)%n", p, n, b, c);
    }

    private static double binomiale(int n, int k) {
        double r = 1;
        for (int i = 0; i < k; i++) r = r * (n - i) / (i + 1);
        return r;
    }

    /**
     * Écrit {@code target/jmh-judge.jsonl} — synthèse par trial.
     * Une ligne difficulty=ALL (agrégée) + une ligne par niveau de difficulté.
     */
    private void writeJudgeResults() {
        try {
            java.nio.file.Path out = java.nio.file.Path.of("benchmarks/jmh-judge.jsonl");
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
        List<RagContextJudge.Judgement> valid = results.stream()
            .map(TrialResult::judgement)
            .filter(j -> !j.isInvalid()).toList();
        if (valid.isEmpty()) return;
        double passRate     = (double) valid.stream().filter(RagContextJudge.Judgement::isPass).count() / valid.size();
        double avgCoverage  = valid.stream().mapToDouble(RagContextJudge.Judgement::hintCoverage).average().orElse(-1);
        double coherence    = (double) valid.stream().filter(RagContextJudge.Judgement::coherent).count() / valid.size();
        double insuffisant  = (double) valid.stream()
            .filter(j -> Boolean.FALSE.equals(j.checks().get("contexte_suffisant"))).count() / valid.size();
        sb.append(String.format(Locale.ROOT,
            "{\"ts\":\"%s\",\"strategy\":\"%s\",\"scenario\":\"%s\",\"fileCount\":%d," +
            "\"difficulty\":\"%s\",\"passRate\":%.3f,\"avgHintCoverage\":%.3f," +
            "\"contexteInsuffisantRate\":%.3f,\"coherenceRate\":%.3f," +
            "\"n\":%d,\"nInvalid\":%d,\"schema\":\"binaire-v1\",\"judgeModel\":\"%s\"}%n",
            java.time.Instant.now(), strategy, scenario, fileCount,
            difficulty, passRate, avgCoverage, insuffisant, coherence,
            valid.size(), results.size() - valid.size(), judgeModelName));
    }

    /**
     * Écrit {@code target/jmh-judge-detail.jsonl} — une ligne par question jugée.
     * Contient : question, difficulté, attendu (expectedFqnHints), généré (contexte retourné), score, rationale.
     * Utilisé par le dashboard pour l'affichage "généré vs attendu vs note".
     */
    private void writeJudgeDetailResults() {
        try {
            java.nio.file.Path out = java.nio.file.Path.of("benchmarks/jmh-judge-detail.jsonl");
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
            RagContextJudge.Judgement j = tr.judgement();
            String generatedCtx = String.join("\n---\n", tr.context());
            if (generatedCtx.length() > 3000) {
                generatedCtx = generatedCtx.substring(0, 3000) + "\n[...]";
            }
            String expectedJson = Arrays.stream(tr.question().expectedFqnHints())
                .map(h -> "\"" + jsonEscape(h) + "\"")
                .collect(Collectors.joining(",", "[", "]"));
            // Les contrôles atomiques sont écrits un par un : c'est eux qui disent *quel*
            // critère la stratégie rate, là où le seul verdict ne dit que qu'elle rate.
            String checksJson = RagContextJudge.CONTROLES.stream()
                .map(c -> "\"" + c + "\":" + j.checks().getOrDefault(c, false))
                .collect(Collectors.joining(",", "{", "}"));
            sb.append(String.format(Locale.ROOT,
                "{\"ts\":\"%s\",\"strategy\":\"%s\",\"scenario\":\"%s\",\"fileCount\":%d," +
                "\"question\":\"%s\",\"difficulty\":\"%s\",\"expected\":%s," +
                "\"generated\":\"%s\",\"verdict\":\"%s\",\"checks\":%s,\"reason\":\"%s\"," +
                "\"hintCoverage\":%.3f,\"coherent\":%b,\"schema\":\"binaire-v1\",\"judgeModel\":\"%s\"}%n",
                java.time.Instant.now(), strategy, scenario, fileCount,
                jsonEscape(tr.question().text()),
                tr.question().difficulty().name(),
                expectedJson,
                jsonEscape(generatedCtx),
                j.verdict(),
                checksJson,
                jsonEscape(j.reason()),
                j.hintCoverage(),
                j.coherent(),
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
