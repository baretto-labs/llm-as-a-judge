package fr.baretto.benchmarks.jmh;

import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.ollama.OllamaChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Juge à verdict binaire, aligné sur le corpus de {@code judge-finetune/}.
 *
 * <p>Remplace {@link LLMJudge}, dont l'échelle 0-10 a été abandonnée le 2026-09-13. Ici le
 * verdict est {@code PASS} <b>si et seulement si</b> les trois contrôles atomiques sont vrais :
 * pas de note, pas de demi-mesure.</p>
 *
 * <p><b>Le contrat d'invite est repris mot pour mot du corpus d'entraînement.</b> Le modèle a été
 * fine-tuné sur cette forme exacte — marqueur {@code TÂCHE:} dans le message système, quatre
 * sections dans le message utilisateur, libellés des critères à l'identique. S'en écarter, même
 * légèrement, c'est interroger le modèle hors de la distribution sur laquelle il a appris.</p>
 *
 * <p>Marqueur retenu : {@code RAG_CONTEXT_RELEVANCE}. C'est celui du corpus qui juge <b>le contexte
 * récupéré</b> et non une réponse générée — exactement ce que fait ce banc d'essai. Sa section
 * {@code ### SORTIE À ÉVALUER} porte une phrase sentinelle qui renvoie au contexte, identique sur
 * les 6 items du golden set ; elle est reproduite telle quelle.</p>
 *
 * <p><b>Pourquoi un appel brut plutôt que {@code AiServices}.</b> La sortie commence par un bloc
 * {@code <thinking>} avant le JSON. La sortie structurée de LangChain4j exige un JSON seul et
 * échouerait. L'analyse est donc tolérante, et reprend la règle déjà éprouvée côté Python :
 * <b>le dernier objet JSON du texte qui porte un {@code verdict}</b>.</p>
 *
 * <p>Configuration, identique à celle de {@link LLMJudge} :</p>
 * <pre>
 *   -Djmh.judge.provider=openai|ollama   (défaut : openai, le juge étant servi par mlx_lm.server)
 *   -Djmh.judge.url=http://127.0.0.1:8082/v1
 *   -Djmh.judge.model=...
 * </pre>
 */
public class RagContextJudge {

    private static final Logger logger = LoggerFactory.getLogger(RagContextJudge.class);

    private static final String PROVIDER_OLLAMA = "ollama";
    private static final String PROVIDER_OPENAI = "openai";
    private static final String DEFAULT_OPENAI_URL = "http://127.0.0.1:8082/v1";
    private static final String DEFAULT_OLLAMA_URL = "http://localhost:11434";
    private static final String DEFAULT_MODEL = "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit";

    /** Repris mot pour mot du corpus : toute variation sort le modèle de sa distribution. */
    private static final String SYSTEM_PROMPT =
        "Tu es un juge IA ultra-rigoureux. TÂCHE: RAG_CONTEXT_RELEVANCE. "
        + "Analyse la situation pas à pas dans <thinking> avant de rendre ton verdict JSON.";

    /** Sentinelle identique sur les 6 items RAG_CONTEXT_RELEVANCE du golden set. */
    private static final String SENTINELLE_SORTIE =
        "(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur "
        + "de recherche a retournés pour cette requête)";

    /** Libellés des trois contrôles, verbatim. */
    private static final String CRITERES = """
        1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
        2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
        3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.""";

    public static final List<String> CONTROLES =
        List.of("contexte_pertinent", "contexte_suffisant", "bruit_maitrise");

    private static final Pattern VERDICT = Pattern.compile("\"verdict\"\\s*:\\s*\"(PASS|FAIL)\"");
    private static final Pattern CHECK = Pattern.compile("\"(\\w+)\"\\s*:\\s*(true|false)");
    private static final Pattern REASON = Pattern.compile("\"reason\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");

    private final ChatModel model;
    private final String modelLabel;

    public RagContextJudge() {
        String provider = System.getProperty("jmh.judge.provider", PROVIDER_OPENAI);
        boolean openai = PROVIDER_OPENAI.equalsIgnoreCase(provider);
        String baseUrl = System.getProperty("jmh.judge.url",
            openai ? DEFAULT_OPENAI_URL : DEFAULT_OLLAMA_URL);
        String modelName = System.getProperty("jmh.judge.model", DEFAULT_MODEL);

        this.model = openai
            ? OpenAiChatModel.builder()
                .baseUrl(baseUrl).apiKey("none").modelName(modelName)
                .temperature(0.0).timeout(Duration.ofSeconds(120)).build()
            : OllamaChatModel.builder()
                .baseUrl(baseUrl).modelName(modelName)
                .temperature(0.0).timeout(Duration.ofSeconds(120)).build();
        this.modelLabel = modelName;
        logger.info("RagContextJudge initialisé : {} sur {} (provider={})", modelName, baseUrl, provider);
    }

    /** Injection directe, pour les tests. */
    public RagContextJudge(ChatModel model) {
        this.model = model;
        this.modelLabel = "injected";
    }

    public String getModelLabel() {
        return modelLabel;
    }

    // ── Résultat ──────────────────────────────────────────────────────────

    /**
     * @param checks        contrôles atomiques ; vide si la sortie n'était pas analysable
     * @param verdict       {@code PASS}, {@code FAIL} ou {@code INVALID}
     * @param reason        justification en une phrase rendue par le juge
     * @param hintCoverage  fraction des indices attendus présents dans le contexte —
     *                      calcul déterministe, sans LLM, donc utilisable comme recoupement
     * @param coherent      le verdict respecte-t-il la règle PASS ⟺ tous les contrôles vrais
     */
    public record Judgement(
        Map<String, Boolean> checks,
        String verdict,
        String reason,
        double hintCoverage,
        boolean coherent
    ) {
        public boolean isPass()    { return "PASS".equals(verdict); }
        public boolean isInvalid() { return INVALID.equals(verdict); }
    }

    public static final String INVALID = "INVALID";

    // ── API ───────────────────────────────────────────────────────────────

    /**
     * Juge la pertinence du contexte récupéré pour répondre à la question.
     *
     * <p>L'ordre des extraits est mélangé avant jugement, pour atténuer le biais de position.</p>
     */
    public Judgement judge(String question, List<String> retrievedContext, String[] expectedHints) {
        if (retrievedContext.isEmpty()) {
            return new Judgement(Map.of(), "FAIL", "Aucun contexte retourné", 0.0, true);
        }

        List<String> shuffled = new ArrayList<>(retrievedContext);
        Collections.shuffle(shuffled);
        String contextText = String.join("\n---\n", shuffled);
        if (contextText.length() > 6000) {
            contextText = contextText.substring(0, 6000) + "\n[... truncated ...]";
        }
        double hintCoverage = computeHintCoverage(contextText, expectedHints);

        String user = """
            ### CONTEXTE / RAG
            %s

            ### ENTREE / REQUÊTE
            %s

            ### SORTIE À ÉVALUER
            %s

            ### CRITÈRES DE VALIDATION
            %s""".formatted(contextText, question, SENTINELLE_SORTIE, CRITERES);

        String raw;
        try {
            ChatResponse response = model.chat(List.<ChatMessage>of(
                SystemMessage.from(SYSTEM_PROMPT), UserMessage.from(user)));
            AiMessage message = response.aiMessage();
            raw = message == null ? "" : message.text();
        } catch (Exception e) {
            logger.warn("Juge en échec sur '{}' : {}", question, e.getMessage());
            return new Judgement(Map.of(), INVALID, "Appel en échec : " + e.getMessage(), hintCoverage, false);
        }
        return parse(raw, hintCoverage);
    }

    /**
     * Analyse tolérante : le dernier objet JSON portant un {@code verdict}.
     *
     * <p>Écrit à la main plutôt que délégué à une sortie structurée, parce que la réponse est
     * précédée d'un bloc {@code <thinking>} qu'aucun analyseur strict n'accepte. Une sortie
     * inexploitable vaut {@code INVALID} et compte comme un désaccord — jamais comme un PASS.</p>
     */
    static Judgement parse(String texte, double hintCoverage) {
        if (texte == null || texte.isBlank()) {
            return new Judgement(Map.of(), INVALID, "Réponse vide", hintCoverage, false);
        }
        int debut = texte.lastIndexOf('{');
        while (debut >= 0) {
            String candidat = texte.substring(debut);
            Matcher mv = VERDICT.matcher(candidat);
            if (mv.find()) {
                String verdict = mv.group(1);

                Map<String, Boolean> checks = new LinkedHashMap<>();
                Matcher mc = CHECK.matcher(candidat);
                while (mc.find()) {
                    checks.put(mc.group(1), Boolean.parseBoolean(mc.group(2)));
                }

                Matcher mr = REASON.matcher(candidat);
                String reason = mr.find() ? mr.group(1).replace("\\\"", "\"").replace("\\n", " ") : "";

                // PASS ⟺ tous les contrôles vrais. Un modèle qui rend PASS avec un contrôle
                // faux s'est contredit : on le relève au lieu de le corriger en silence, parce
                // que c'est une mesure de la qualité du juge, pas un défaut à masquer.
                boolean coherent = !checks.isEmpty()
                    && checks.values().stream().allMatch(Boolean::booleanValue) == "PASS".equals(verdict);

                return new Judgement(Map.copyOf(checks), verdict, reason, hintCoverage, coherent);
            }
            debut = texte.lastIndexOf('{', debut - 1);
        }
        return new Judgement(Map.of(), INVALID, "Aucun verdict analysable", hintCoverage, false);
    }

    /** Déterministe, sans LLM : c'est ce qui en fait un recoupement du juge et non un doublon. */
    static double computeHintCoverage(String contextText, String[] hints) {
        if (hints == null || hints.length == 0) return 1.0;
        String lower = contextText.toLowerCase();
        long found = 0;
        for (String hint : hints) {
            if (lower.contains(hint.toLowerCase())) found++;
        }
        return (double) found / hints.length;
    }
}
