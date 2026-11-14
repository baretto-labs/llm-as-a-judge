package fr.baretto.benchmarks.jmh;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import java.io.BufferedWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Second temps de la campagne RAG : <b>juger</b> ce que {@link RagCampaignGenerate} a écrit.
 * Rien n'est récupéré ni généré ici.
 *
 * <p>Deux verdicts par ligne, comme dans {@link RagQualityEvaluation} :</p>
 *
 * <ul>
 *   <li><b>contexte</b> ({@link RagContextJudge}, {@code RAG_CONTEXT_RELEVANCE}) — le moteur
 *       a-t-il ramené de quoi répondre ;</li>
 *   <li><b>réponse</b> ({@link RagAnswerJudge}, {@code RAG_FAITHFULNESS}) — la réponse s'en
 *       tient-elle au contexte qu'elle a reçu.</li>
 * </ul>
 *
 * <p><b>Ce que cette classe permet, et ce qu'elle ne permet pas.</b> Elle se relance autant de
 * fois qu'il y a de juges, sur le <b>même</b> fichier de générations, et écrit un fichier par
 * juge. Faire tourner deux juges mesure donc leur <b>accord</b> sur des réponses identiques.
 * Cela ne mesure <b>pas</b> leur justesse : les réponses de la campagne RAG n'ont aucune
 * étiquette de référence. Seul l'étalon {@code data/golden/test.jsonl} en a, et c'est le seul
 * endroit où un juge peut être dit faux. Un désaccord lu ici dit que les deux juges divergent,
 * jamais lequel a raison.</p>
 *
 * <pre>
 *   mvn test -Dtest=RagCampaignJudge \
 *     -Drag.campaign.file=benchmarks/rag-campaign.jsonl \
 *     -Drag.campaign.judge.label=32B-conventions \
 *     -Djmh.judge.url=http://127.0.0.1:8083/v1 \
 *     -Djmh.answerjudge.url=http://127.0.0.1:8083/v1
 * </pre>
 *
 * <p>L'étiquette {@code rag.campaign.judge.label} nomme le fichier de sortie et figure dans
 * chaque ligne : c'est elle, et non l'identifiant du modèle, qui sert de clé de comparaison
 * entre juges.</p>
 */
@Tag("benchmark")
class RagCampaignJudge {

    static final String SCHEMA = "campagne-jugee-v1";

    private static final ObjectMapper JSON = new ObjectMapper();

    /** Une propriété vide vaut absente : surefire les transmet toutes, y compris non renseignées. */
    private static String prop(String cle, String defaut) {
        String v = System.getProperty(cle);
        return (v == null || v.isBlank()) ? defaut : v.trim();
    }

    @Test
    void jugeLaCampagne() throws Exception {
        Path entree = Path.of(prop("rag.campaign.file",
            RagCampaignGenerate.SORTIE_PAR_DEFAUT.toString()));
        if (!Files.isRegularFile(entree)) {
            throw new IllegalStateException(
                entree + " introuvable : lance d'abord RagCampaignGenerate.");
        }

        String etiquette = prop("rag.campaign.judge.label", null);
        if (etiquette == null) {
            throw new IllegalStateException(
                "-Drag.campaign.judge.label est obligatoire : c'est cette étiquette qui distingue "
                + "les passes de deux juges sur les mêmes générations. Sans elle, la seconde passe "
                + "écraserait la première ou s'y mélangerait.");
        }

        Path sortie = entree.resolveSibling(
            entree.getFileName().toString().replaceFirst("\\.jsonl$", "")
            + "-juge-" + etiquette + ".jsonl");
        if (Files.exists(sortie)) {
            throw new IllegalStateException(
                sortie + " existe déjà : cette étiquette a déjà jugé ce fichier. Déplace-le ou "
                + "change -Drag.campaign.judge.label.");
        }

        List<ObjectNode> generations = new ArrayList<>();
        for (String l : Files.readAllLines(entree)) {
            if (!l.isBlank()) generations.add((ObjectNode) JSON.readTree(l));
        }
        if (generations.isEmpty()) {
            throw new IllegalStateException(entree + " ne contient aucune ligne.");
        }

        var jugeContexte = new RagContextJudge();
        var jugeReponse  = new RagAnswerJudge();

        System.out.printf("[Juge] entrée=%s  lignes=%d%n", entree, generations.size());
        System.out.printf("[Juge] étiquette=%s  contexte=%s  réponse=%s%n",
            etiquette, jugeContexte.getModelLabel(), jugeReponse.getModelLabel());
        System.out.printf("[Juge] sortie : %s%n", sortie);

        List<ObjectNode> jugees = new ArrayList<>();
        try (BufferedWriter out = Files.newBufferedWriter(sortie,
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            int i = 0;
            for (ObjectNode g : generations) {
                i++;
                String question = g.get("question").asText();
                String[] indices = indices(g.get("expected"));
                List<String> contexte = textes(g.get("context"));

                var jc = jugeContexte.judge(question, contexte, indices);
                // Le juge de fidélité reçoit le contexte EXACT soumis au générateur, jamais la
                // liste brute : sinon il sanctionnerait comme invention une phrase tirée d'un
                // extrait qu'il n'aurait pas reçu.
                var jr = jugeReponse.judge(question, g.get("answerContext").asText(),
                    g.get("answer").asText(), indices);

                ObjectNode n = g.deepCopy();
                n.put("schema", SCHEMA);
                n.put("judgeLabel", etiquette);
                n.put("judgedTs", Instant.now().toString());
                n.put("contextJudgeModel", jugeContexte.getModelLabel());
                n.put("answerJudgeModel", jugeReponse.getModelLabel());
                verdict(n, "context", jc, RagContextJudge.CONTROLES);
                verdict(n, "answer", jr, RagAnswerJudge.CONTROLES);
                // Le contexte intégral a servi au jugement, il n'a plus à être recopié : la
                // ligne jugée reste diffable, et la génération demeure dans son fichier.
                n.remove("context");

                out.write(JSON.writeValueAsString(n));
                out.write('\n');
                out.flush(); // un jugement perdu est un jugement à repayer
                jugees.add(n);
                System.out.printf("  [%3d/%d] %-12s %-48s ctx=%-7s rep=%-7s%n",
                    i, generations.size(), g.get("arm").asText(),
                    question.substring(0, Math.min(48, question.length())),
                    jc.verdict(), jr.verdict());
            }
        }

        resume(jugees, etiquette);
        System.out.printf("%n[Juge] écrit : %s%n", sortie);
    }

    private static void verdict(ObjectNode n, String prefixe, RagContextJudge.Judgement j,
                                List<String> controles) {
        n.put(prefixe + "Verdict", j.verdict());
        ObjectNode checks = n.putObject(prefixe + "Checks");
        for (String c : controles) checks.put(c, j.checks().getOrDefault(c, false));
        n.put(prefixe + "Reason", j.reason());
        n.put(prefixe + "HintCoverage", j.hintCoverage());
        n.put(prefixe + "Coherent", j.coherent());
    }

    private static String[] indices(JsonNode tableau) {
        if (tableau == null || !tableau.isArray()) return new String[0];
        List<String> out = new ArrayList<>();
        for (JsonNode n : (ArrayNode) tableau) out.add(n.asText());
        return out.toArray(new String[0]);
    }

    private static List<String> textes(JsonNode tableau) {
        List<String> out = new ArrayList<>();
        if (tableau != null && tableau.isArray()) {
            for (JsonNode n : (ArrayNode) tableau) out.add(n.asText());
        }
        return out;
    }

    /**
     * Compte rendu par bras. Les INVALID sont comptés à part et jamais fondus dans les FAIL :
     * un juge qui n'a pas rendu de JSON exploitable n'a pas constaté un échec de la stratégie.
     */
    private static void resume(List<ObjectNode> lignes, String etiquette) {
        Map<String, int[]> parBras = new LinkedHashMap<>();
        for (ObjectNode n : lignes) {
            // [0] total, [1] ctx PASS, [2] ctx INVALID, [3] rep PASS, [4] rep INVALID
            int[] c = parBras.computeIfAbsent(n.get("arm").asText(), k -> new int[5]);
            c[0]++;
            String vc = n.get("contextVerdict").asText();
            String vr = n.get("answerVerdict").asText();
            if ("PASS".equals(vc)) c[1]++;
            if (RagContextJudge.INVALID.equals(vc)) c[2]++;
            if ("PASS".equals(vr)) c[3]++;
            if (RagContextJudge.INVALID.equals(vr)) c[4]++;
        }
        System.out.printf("%n── Juge %s ──────────────────────────────────────────%n", etiquette);
        System.out.printf("%-14s %6s %14s %10s %14s %10s%n",
            "bras", "n", "contexte PASS", "ctx INV.", "réponse PASS", "rep INV.");
        for (var e : parBras.entrySet()) {
            int[] c = e.getValue();
            System.out.printf(Locale.ROOT, "%-14s %6d %13.1f%% %10d %13.1f%% %10d%n",
                e.getKey(), c[0], 100.0 * c[1] / c[0], c[2], 100.0 * c[3] / c[0], c[4]);
        }
    }
}
