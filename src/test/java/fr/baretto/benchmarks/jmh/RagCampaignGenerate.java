package fr.baretto.benchmarks.jmh;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import fr.baretto.benchmarks.strategy.FeatureFlags;
import fr.baretto.benchmarks.strategy.LuceneRagStrategy;
import fr.baretto.benchmarks.strategy.Neo4jGraphRagStrategy;
import fr.baretto.benchmarks.strategy.RagStrategy;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import java.io.BufferedWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;

/**
 * Premier temps de la campagne RAG : <b>récupérer et répondre</b>, puis tout écrire. Aucun juge
 * n'est appelé ici.
 *
 * <p><b>Pourquoi la boucle est coupée en deux.</b> {@link RagQualityEvaluation} génère et juge
 * dans la même itération. Tant qu'il y avait deux bras et un juge, cela tenait. La campagne du
 * talk en demande trois, jugés par au moins deux juges — et deux contraintes rendent la boucle
 * unique intenable :</p>
 *
 * <ul>
 *   <li><b>La mémoire.</b> Le générateur retenu pèse ~18 Go servi par Ollama, le juge 32B
 *       ~18,4 Go servi par {@code mlx_lm.server}. Les deux ne tiennent pas résidents ensemble
 *       sous 27 Go utilisables ; les faire charger et décharger à chaque question coûterait plus
 *       cher que toute l'inférence.</li>
 *   <li><b>Le coût du second juge.</b> Rejuger avec un deuxième modèle ne doit pas re-générer
 *       180 réponses. Les générations sont le poste cher et elles ne dépendent d'aucun juge :
 *       une fois persistées, chaque juge supplémentaire ne paie que ses propres appels.</li>
 * </ul>
 *
 * <p>Ce fichier JSONL est donc l'<b>entrée figée</b> de {@link RagCampaignJudge} : les trois bras
 * voient exactement les mêmes questions, et tous les juges voient exactement les mêmes réponses.
 * C'est cette identité-là qui autorise à parler d'accord entre juges.</p>
 *
 * <p><b>Les trois bras</b>, déclarés avant exécution et nommés comme à l'écran :</p>
 *
 * <pre>
 *   vector        LuceneRagStrategy      preset knn-only      vectoriel seul
 *   vector-bm25   LuceneRagStrategy      preset hybrid        vectoriel + BM25
 *   graphrag      Neo4jGraphRagStrategy  preset hybrid-graph  GraphRAG
 * </pre>
 *
 * <p>Chaque bras a son propre index, construit dans son propre répertoire temporaire : un bras ne
 * peut pas hériter de l'état d'un autre.</p>
 *
 * <pre>
 *   mvn test -Dtest=RagCampaignGenerate \
 *     -Drag.source.dir=/chemin/vers/OllamAssist/src/main/java \
 *     -Drag.answer.model=qwen3.8:27b
 * </pre>
 *
 * <p>Le fichier de sortie n'est jamais écrasé : il porte des heures d'inférence. Si le chemin
 * existe, le test échoue et demande un autre nom.</p>
 *
 * <p><b>Deux leviers de sonde</b>, pour vérifier la chaîne avant d'engager les 180 générations.
 * Ils ne servent qu'à cela : toute campagne publiée les laisse à leur défaut, et le fichier
 * produit porte de toute façon son bras et son nombre de lignes.</p>
 *
 * <pre>
 *   -Drag.campaign.limit=1            n premières questions seulement
 *   -Drag.campaign.arms=vector        bras à exécuter, séparés par des virgules
 * </pre>
 */
@Tag("benchmark")
class RagCampaignGenerate {

    static final Path SORTIE_PAR_DEFAUT = Path.of("benchmarks/rag-campaign.jsonl");
    static final String SCHEMA = "campagne-v1";

    /** Bras de la campagne : nom à l'écran, moteur, préréglage. */
    record Bras(String nom, String moteur, String preset) {}

    static final List<Bras> BRAS = List.of(
        new Bras("vector",      "lucene", "knn-only"),
        new Bras("vector-bm25", "lucene", "hybrid"),
        new Bras("graphrag",    "neo4j",  "hybrid-graph"));

    private static final ObjectMapper JSON = new ObjectMapper();

    /** Une propriété vide vaut absente : surefire les transmet toutes, y compris non renseignées. */
    private static String prop(String cle, String defaut) {
        String v = System.getProperty(cle);
        return (v == null || v.isBlank()) ? defaut : v.trim();
    }

    @Test
    void genereLesTroisBras() throws Exception {
        String source = prop("rag.source.dir", null);
        // Échec franc, jamais un repli silencieux sur le corpus synthétique : c'est ce qui avait
        // invalidé le run du 2026-09-21, où les questions portaient sur OllamAssist et le
        // contexte récupéré venait de `com.example.service.Class0Service`.
        if (source == null) {
            throw new IllegalStateException(
                "-Drag.source.dir est obligatoire : sans lui l'indexation porterait sur un corpus "
                + "synthétique sans rapport avec les questions, et toutes les mesures seraient nulles.");
        }
        Path sourceDir = Path.of(source);
        if (!Files.isDirectory(sourceDir)) {
            throw new IllegalStateException("répertoire source introuvable : " + sourceDir);
        }

        Path sortie = Path.of(prop("rag.campaign.file", SORTIE_PAR_DEFAUT.toString()));
        if (Files.exists(sortie)) {
            throw new IllegalStateException(
                sortie + " existe déjà. Ce fichier porte des heures de génération et n'est jamais "
                + "écrasé : déplace-le, ou passe -Drag.campaign.file=<autre chemin>.");
        }
        Files.createDirectories(sortie.toAbsolutePath().getParent());

        String filtre = prop("jmh.difficulty", null);
        List<QuestionCorpus.Question> questions = filtre == null
            ? QuestionCorpus.QUESTIONS
            : QuestionCorpus.QUESTIONS.stream()
                .filter(q -> q.difficulty().name().equalsIgnoreCase(filtre)).toList();

        int limite = Integer.parseInt(prop("rag.campaign.limit", "0"));
        if (limite > 0 && limite < questions.size()) questions = questions.subList(0, limite);

        String brasDemandes = prop("rag.campaign.arms", null);
        List<Bras> bras = brasDemandes == null ? BRAS : BRAS.stream()
            .filter(b -> List.of(brasDemandes.split(",")).contains(b.nom())).toList();
        if (bras.isEmpty()) {
            throw new IllegalStateException("-Drag.campaign.arms=" + brasDemandes
                + " ne désigne aucun bras connu parmi "
                + BRAS.stream().map(Bras::nom).toList());
        }

        var repondeur = new RagAnswerer();
        String runId = Instant.now().toString();

        System.out.printf("[Campagne] source=%s  questions=%d  bras=%d  générateur=%s%n",
            sourceDir, questions.size(), bras.size(), repondeur.getModelLabel());
        System.out.printf("[Campagne] sortie : %s  (runId %s)%n", sortie, runId);

        try (BufferedWriter out = Files.newBufferedWriter(sortie,
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {

            for (Bras b : bras) {
                // Un index par bras, dans son propre répertoire : aucun état ne traverse.
                Path dir = Files.createTempDirectory("campagne-" + b.nom() + "-");
                FeatureFlags flags = FeatureFlags.fromPreset(b.preset());
                RagStrategy strategie = "neo4j".equals(b.moteur())
                    ? new Neo4jGraphRagStrategy(dir.toString(), flags)
                    : new LuceneRagStrategy(dir, flags);
                try {
                    long t0 = System.currentTimeMillis();
                    System.out.printf("[%s] indexation (%s, preset %s)…%n",
                        b.nom(), b.moteur(), b.preset());
                    strategie.indexDirectory(sourceDir);
                    System.out.printf("[%s] indexée en %d s%n",
                        b.nom(), (System.currentTimeMillis() - t0) / 1000);

                    int i = 0;
                    for (QuestionCorpus.Question q : questions) {
                        i++;
                        List<String> ctx = strategie.retrieveContext(q.text());
                        RagAnswerer.Answer a = repondeur.answer(q.text(), ctx);
                        out.write(ligne(runId, b, q, ctx, a, repondeur.getModelLabel()));
                        out.write('\n');
                        out.flush(); // une génération perdue est une génération à repayer
                        System.out.printf("  [%s %2d/%d] %-52s  extraits=%-2d  %5d ms%s%n",
                            b.nom(), i, questions.size(),
                            q.text().substring(0, Math.min(52, q.text().length())),
                            ctx.size(), a.millis(), a.echec() ? "  ÉCHEC" : "");
                    }
                } finally {
                    strategie.close();
                    supprime(dir);
                }
            }
        }

        System.out.printf("%n[Campagne] écrit : %s%n", sortie);
        System.out.printf("[Campagne] juger ensuite : mvn test -Dtest=RagCampaignJudge "
            + "-Drag.campaign.file=%s -Drag.campaign.judge.label=<nom du juge>%n", sortie);
    }

    /**
     * Le contexte est persisté <b>entier</b>, extrait par extrait, et jamais tronqué : ce fichier
     * n'est pas un journal de lecture mais l'entrée du juge. {@code answerContext} porte en plus
     * la chaîne exacte soumise au générateur (plafonnée par {@link RagAnswerer}), celle que le
     * juge de fidélité doit recevoir telle quelle.
     */
    private static String ligne(String runId, Bras b, QuestionCorpus.Question q,
                                List<String> ctx, RagAnswerer.Answer a, String modele)
            throws Exception {
        ObjectNode n = JSON.createObjectNode();
        n.put("schema", SCHEMA);
        n.put("runId", runId);
        n.put("ts", Instant.now().toString());
        n.put("arm", b.nom());
        n.put("engine", b.moteur());
        n.put("preset", b.preset());
        n.put("question", q.text());
        n.put("difficulty", q.difficulty().name());
        ArrayNode attendu = n.putArray("expected");
        for (String h : q.expectedFqnHints()) attendu.add(h);
        ArrayNode extraits = n.putArray("context");
        for (String c : ctx) extraits.add(c);
        n.put("contextChunks", ctx.size());
        n.put("answerContext", a.contexte());
        n.put("answer", a.texte());
        n.put("answerMillis", a.millis());
        n.put("answerFailed", a.echec());
        n.put("answerModel", modele);
        return JSON.writeValueAsString(n);
    }

    private static void supprime(Path dir) throws Exception {
        if (dir == null || !Files.exists(dir)) return;
        try (var flux = Files.walk(dir)) {
            flux.sorted(Comparator.reverseOrder()).forEach(p -> {
                try { Files.delete(p); } catch (Exception ignored) { }
            });
        }
    }
}
