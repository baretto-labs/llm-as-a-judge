package fr.baretto.benchmarks.jmh;

import fr.baretto.benchmarks.strategy.FeatureFlags;
import fr.baretto.benchmarks.strategy.LuceneRagStrategy;
import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertFalse;

/**
 * Évaluation de la qualité des stratégies RAG, jugée par {@link RagContextJudge}.
 *
 * <p><b>Volontairement hors de JMH.</b> Le jugement avait été greffé dans
 * {@code RetrievalBenchmark}, en {@code @TearDown(Level.Trial)}, et cela a produit deux défauts
 * mesurés le 2026-09-21 :</p>
 *
 * <ul>
 *   <li><b>L'échéance de JMH interrompait le jugement à mi-parcours.</b> Délai par défaut de
 *       10 minutes par itération ; à ~20 s l'appel, 24 jugements l'épuisaient. Le motif d'échec
 *       était rigoureusement contigu — 24 jugements propres puis 36 échecs d'affilée — et
 *       70 jugements sur 120 sont ressortis INVALID.</li>
 *   <li><b>L'appariement était structurellement impossible.</b> JMH exécute chaque méthode
 *       {@code @Benchmark} dans son propre essai, si bien que les résultats Lucene et Neo4j
 *       n'ont jamais coexisté : « Batch judging 60 Lucene + 0 Neo4j », puis l'inverse. McNemar
 *       ne trouvait aucune paire et ne pouvait rien conclure.</li>
 * </ul>
 *
 * <p>Juger n'est pas un microbenchmark. JMH mesure des latences ; la qualité se mesure ici, dans
 * une boucle ordinaire où les deux stratégies répondent à la <b>même</b> question l'une après
 * l'autre — ce qui rend le test apparié possible, et supprime toute échéance.</p>
 *
 * <pre>
 *   mvn test -Dtest=RagQualityEvaluation \
 *     -Drag.source.dir=/chemin/vers/OllamAssist/src/main/java \
 *     -Djmh.judge.url=http://127.0.0.1:8082/v1
 * </pre>
 */
@Tag("benchmark")
class RagQualityEvaluation {

    private static final Path SORTIE = Path.of("benchmarks");
    private static final String SCHEMA = "binaire-v1";

    /** Une propriété vide vaut absente : surefire les transmet toutes, y compris non renseignées. */
    private static String prop(String cle, String defaut) {
        String v = System.getProperty(cle);
        return (v == null || v.isBlank()) ? defaut : v.trim();
    }

    private record Paire(QuestionCorpus.Question question,
                         List<String> ctxLucene, RagContextJudge.Judgement jLucene,
                         List<String> ctxNeo4j,  RagContextJudge.Judgement jNeo4j) {}

    @Test
    void evalueLesDeuxStrategies() throws Exception {
        String source = prop("rag.source.dir", null);
        // Échec franc, jamais un repli silencieux sur le corpus synthétique : c'est exactement
        // ce qui a invalidé le run du 2026-09-21, où les questions portaient sur OllamAssist et
        // le contexte récupéré venait de `com.example.service.Class0Service`.
        if (source == null) {
            throw new IllegalStateException(
                "-Drag.source.dir est obligatoire : sans lui l'indexation porterait sur un corpus "
                + "synthétique sans rapport avec les questions, et toutes les mesures seraient nulles.");
        }
        Path sourceDir = Path.of(source);
        assertFalse(!Files.isDirectory(sourceDir), "répertoire source introuvable : " + sourceDir);

        String scenario = prop("rag.scenario", "hybrid|hybrid-graph");
        String[] parts = scenario.split("\\|", 2);
        FeatureFlags flagsLucene = FeatureFlags.fromPreset(parts[0]);
        FeatureFlags flagsNeo4j  = FeatureFlags.fromPreset(parts.length > 1 ? parts[1] : parts[0]);

        String filtre = prop("jmh.difficulty", null);
        List<QuestionCorpus.Question> questions = filtre == null
            ? QuestionCorpus.QUESTIONS
            : QuestionCorpus.QUESTIONS.stream()
                .filter(q -> q.difficulty().name().equalsIgnoreCase(filtre)).toList();

        System.out.printf("[Qualité] source=%s  scenario=%s  questions=%d%n",
            sourceDir, scenario, questions.size());

        Path dirLucene = Files.createTempDirectory("qualite-lucene-");
        Path dirNeo4j  = Files.createTempDirectory("qualite-neo4j-");
        var lucene = new LuceneRagStrategy(dirLucene, flagsLucene);
        var neo4j  = new Neo4jGraphRagStrategy(dirNeo4j.toString(), flagsNeo4j);
        var judge  = new RagContextJudge();
        List<Paire> paires = new ArrayList<>();

        try {
            long t0 = System.currentTimeMillis();
            System.out.println("[Qualité] indexation Lucene…");
            lucene.indexDirectory(sourceDir);
            System.out.println("[Qualité] indexation Neo4j…");
            neo4j.indexDirectory(sourceDir);
            System.out.printf("[Qualité] indexation terminée en %d s%n", (System.currentTimeMillis() - t0) / 1000);

            int i = 0;
            for (QuestionCorpus.Question q : questions) {
                i++;
                // Les deux stratégies répondent à la MÊME question dans la même itération :
                // c'est ce qui rend le test apparié possible.
                List<String> cl = lucene.retrieveContext(q.text());
                List<String> cn = neo4j.retrieveContext(q.text());
                var jl = judge.judge(q.text(), cl, q.expectedFqnHints());
                var jn = judge.judge(q.text(), cn, q.expectedFqnHints());
                paires.add(new Paire(q, cl, jl, cn, jn));
                System.out.printf("  [%2d/%d] %-58s lucene=%-7s neo4j=%-7s%n",
                    i, questions.size(), q.text().substring(0, Math.min(58, q.text().length())),
                    jl.verdict(), jn.verdict());
            }
        } finally {
            lucene.close();
            neo4j.close();
            supprime(dirLucene);
            supprime(dirNeo4j);
        }

        resume(paires, judge.getModelLabel(), scenario);
        ecrisSynthese(paires, judge.getModelLabel(), scenario);
        ecrisDetail(paires, judge.getModelLabel(), scenario);
    }

    // ── Mesures ───────────────────────────────────────────────────────────

    private record McNemar(int b, int c, double p) {}

    /**
     * McNemar exact bilatéral sur les questions où les deux jugements sont exploitables.
     *
     * <p>Seules les paires <b>discordantes</b> portent de l'information. À cet effectif, leur
     * nombre est le vrai déterminant de la puissance — il est publié avec le p.</p>
     */
    private static McNemar mcNemar(List<Paire> paires) {
        int b = 0, c = 0;
        for (Paire p : paires) {
            if (p.jLucene().isInvalid() || p.jNeo4j().isInvalid()) continue;
            boolean l = p.jLucene().isPass(), n = p.jNeo4j().isPass();
            if (l && !n) b++;
            else if (!l && n) c++;
        }
        int n = b + c;
        if (n == 0) return new McNemar(b, c, 1.0);
        double queue = 0;
        for (int i = 0; i <= Math.min(b, c); i++) queue += binomiale(n, i);
        return new McNemar(b, c, Math.min(1.0, 2 * queue / Math.pow(2, n)));
    }

    private static double binomiale(int n, int k) {
        double r = 1;
        for (int i = 0; i < k; i++) r = r * (n - i) / (i + 1);
        return r;
    }

    private static double tauxPass(List<RagContextJudge.Judgement> js) {
        var valides = js.stream().filter(j -> !j.isInvalid()).toList();
        return valides.isEmpty() ? Double.NaN
            : (double) valides.stream().filter(RagContextJudge.Judgement::isPass).count() / valides.size();
    }

    private void resume(List<Paire> paires, String modele, String scenario) {
        var jl = paires.stream().map(Paire::jLucene).toList();
        var jn = paires.stream().map(Paire::jNeo4j).toList();
        var mc = mcNemar(paires);
        System.out.println("\n[Qualité] ── résultats ──");
        System.out.printf("  scenario   : %s   juge : %s%n", scenario, modele);
        for (var e : Map.of("lucene", jl, "neo4j", jn).entrySet()) {
            var js = e.getValue();
            long inval = js.stream().filter(RagContextJudge.Judgement::isInvalid).count();
            double cov = js.stream().mapToDouble(RagContextJudge.Judgement::hintCoverage).average().orElse(Double.NaN);
            System.out.printf("  %-7s    pass=%.1f%%  hintCoverage=%.3f  invalides=%d/%d%n",
                e.getKey(), tauxPass(js) * 100, cov, inval, js.size());
        }
        System.out.printf("  McNemar    : p=%.4f sur %d paires discordantes "
                + "(lucene seul PASS %d, neo4j seul PASS %d)%n", mc.p(), mc.b() + mc.c(), mc.b(), mc.c());
        if (mc.b() + mc.c() == 0) {
            System.out.println("  → aucune paire discordante : les deux stratégies s'accordent partout, "
                + "rien à conclure sur leur différence.");
        }
    }

    // ── Écriture ──────────────────────────────────────────────────────────

    private void ecrisSynthese(List<Paire> paires, String modele, String scenario) throws Exception {
        Files.createDirectories(SORTIE);
        StringBuilder sb = new StringBuilder();
        var mc = mcNemar(paires);
        for (String strat : new String[]{"lucene", "neo4j"}) {
            ligneSynthese(sb, paires, strat, "ALL", modele, scenario, mc);
            for (QuestionCorpus.Difficulty d : QuestionCorpus.Difficulty.values()) {
                var sous = paires.stream().filter(p -> p.question().difficulty() == d).toList();
                if (!sous.isEmpty()) ligneSynthese(sb, sous, strat, d.name(), modele, scenario, mcNemar(sous));
            }
        }
        Files.writeString(SORTIE.resolve("rag-quality.jsonl"), sb.toString(),
            StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        System.out.println("  écrit : benchmarks/rag-quality.jsonl");
    }

    private void ligneSynthese(StringBuilder sb, List<Paire> paires, String strat, String diff,
                               String modele, String scenario, McNemar mc) {
        var js = paires.stream().map(p -> strat.equals("lucene") ? p.jLucene() : p.jNeo4j()).toList();
        var valides = js.stream().filter(j -> !j.isInvalid()).toList();
        if (valides.isEmpty()) return;
        double insuffisant = (double) valides.stream()
            .filter(j -> Boolean.FALSE.equals(j.checks().get("contexte_suffisant"))).count() / valides.size();
        sb.append(String.format(Locale.ROOT,
            "{\"ts\":\"%s\",\"strategy\":\"%s\",\"scenario\":\"%s\",\"difficulty\":\"%s\","
            + "\"passRate\":%.3f,\"avgHintCoverage\":%.3f,\"contexteInsuffisantRate\":%.3f,"
            + "\"coherenceRate\":%.3f,\"n\":%d,\"nInvalid\":%d,"
            + "\"mcnemarP\":%.4f,\"discordantes\":%d,\"luceneSeulPass\":%d,\"neo4jSeulPass\":%d,"
            + "\"schema\":\"%s\",\"judgeModel\":\"%s\"}%n",
            java.time.Instant.now(), strat, scenario, diff,
            tauxPass(js),
            js.stream().mapToDouble(RagContextJudge.Judgement::hintCoverage).average().orElse(-1),
            insuffisant,
            (double) valides.stream().filter(RagContextJudge.Judgement::coherent).count() / valides.size(),
            valides.size(), js.size() - valides.size(),
            mc.p(), mc.b() + mc.c(), mc.b(), mc.c(), SCHEMA, modele));
    }

    private void ecrisDetail(List<Paire> paires, String modele, String scenario) throws Exception {
        StringBuilder sb = new StringBuilder();
        for (Paire p : paires) {
            ligneDetail(sb, p, "lucene", p.ctxLucene(), p.jLucene(), modele, scenario);
            ligneDetail(sb, p, "neo4j",  p.ctxNeo4j(),  p.jNeo4j(),  modele, scenario);
        }
        Files.writeString(SORTIE.resolve("rag-quality-detail.jsonl"), sb.toString(),
            StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        System.out.println("  écrit : benchmarks/rag-quality-detail.jsonl");
    }

    private void ligneDetail(StringBuilder sb, Paire p, String strat, List<String> ctx,
                             RagContextJudge.Judgement j, String modele, String scenario) {
        String genere = String.join("\n---\n", ctx);
        if (genere.length() > 3000) genere = genere.substring(0, 3000) + "\n[...]";
        String attendu = java.util.Arrays.stream(p.question().expectedFqnHints())
            .map(h -> "\"" + echappe(h) + "\"").collect(Collectors.joining(",", "[", "]"));
        // Les contrôles un par un : c'est eux qui disent *quel* critère la stratégie rate.
        String checks = RagContextJudge.CONTROLES.stream()
            .map(c -> "\"" + c + "\":" + j.checks().getOrDefault(c, false))
            .collect(Collectors.joining(",", "{", "}"));
        sb.append(String.format(Locale.ROOT,
            "{\"ts\":\"%s\",\"strategy\":\"%s\",\"scenario\":\"%s\",\"question\":\"%s\","
            + "\"difficulty\":\"%s\",\"expected\":%s,\"generated\":\"%s\",\"verdict\":\"%s\","
            + "\"checks\":%s,\"reason\":\"%s\",\"hintCoverage\":%.3f,\"coherent\":%b,"
            + "\"schema\":\"%s\",\"judgeModel\":\"%s\"}%n",
            java.time.Instant.now(), strat, scenario, echappe(p.question().text()),
            p.question().difficulty().name(), attendu, echappe(genere), j.verdict(),
            checks, echappe(j.reason()), j.hintCoverage(), j.coherent(), SCHEMA, modele));
    }

    private static String echappe(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t");
    }

    private static void supprime(Path dir) throws Exception {
        if (dir == null || !Files.exists(dir)) return;
        try (var flux = Files.walk(dir)) {
            flux.sorted(Comparator.reverseOrder()).forEach(p -> {
                try { Files.delete(p); } catch (Exception ignored) { }
            });
        }
    }

    /** Conservé pour que la carte des contrôles reste ordonnée si un appelant l'inspecte. */
    @SuppressWarnings("unused")
    private static Map<String, Boolean> ordonne(Map<String, Boolean> m) {
        var out = new LinkedHashMap<String, Boolean>();
        for (String c : RagContextJudge.CONTROLES) out.put(c, m.getOrDefault(c, false));
        return out;
    }
}
