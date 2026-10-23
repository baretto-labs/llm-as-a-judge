package fr.baretto.benchmarks.jmh;

import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.chat.request.ResponseFormat;
import dev.langchain4j.model.chat.request.ResponseFormatType;
import dev.langchain4j.model.chat.request.json.JsonBooleanSchema;
import dev.langchain4j.model.chat.request.json.JsonEnumSchema;
import dev.langchain4j.model.chat.request.json.JsonObjectSchema;
import dev.langchain4j.model.chat.request.json.JsonSchema;
import dev.langchain4j.model.chat.request.json.JsonStringSchema;
import dev.langchain4j.model.ollama.OllamaChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.List;
import java.util.Map;

/**
 * Juge binaire de la <b>réponse générée</b>, pendant de {@link RagContextJudge} qui, lui, ne juge
 * que le contexte récupéré.
 *
 * <p><b>Le marqueur n'est pas choisi, il existe déjà.</b> Le corpus de {@code judge-finetune/}
 * porte trois tâches, dont {@code RAG_FAITHFULNESS} : « la sortie à évaluer est une réponse
 * rédigée, le contexte est ce qui doit l'étayer ». Message système, intitulés des trois contrôles
 * et structure des quatre sections sont repris <b>mot pour mot</b> d'un item du corpus
 * ({@code b14-011}), pour la même raison que dans {@code RagContextJudge} : une invite reformulée
 * interroge le modèle hors de la distribution sur laquelle le banc a été étalonné.</p>
 *
 * <p><b>Ce que ce juge mesure, et ce qu'il ne mesure pas.</b> {@code RAG_FAITHFULNESS} sanctionne
 * l'invention, pas l'ignorance : une réponse qui dit « le contexte ne permet pas de répondre »
 * est fidèle. Une stratégie de récupération faible produira donc des réponses <i>fidèles et
 * inutiles</i>. C'est pour cela que le verdict de fidélité est publié <b>à côté</b> du verdict de
 * contexte et jamais à sa place : ensemble ils séparent « le moteur n'a rien trouvé » de « le
 * modèle a brodé ».</p>
 *
 * <p>Configuration, délibérément distincte de celle du juge de contexte, pour pouvoir servir les
 * deux juges sur deux ports — ou le même :</p>
 * <pre>
 *   -Djmh.answerjudge.provider=openai|ollama
 *   -Djmh.answerjudge.url=http://127.0.0.1:8083/v1
 *   -Djmh.answerjudge.model=mlx-community/Qwen2.5-Coder-32B-Instruct-4bit
 *   -Djmh.answerjudge.adapter=        (vide par défaut : aucun adaptateur)
 *   -Djmh.answerjudge.suffix=judge-finetune/configs/conventions.md
 * </pre>
 */
public class RagAnswerJudge {

    private static final Logger logger = LoggerFactory.getLogger(RagAnswerJudge.class);

    private static final String PROVIDER_OPENAI = "openai";
    private static final String DEFAULT_OPENAI_URL = "http://127.0.0.1:8083/v1";
    private static final String DEFAULT_OLLAMA_URL = "http://localhost:11434";

    /**
     * Qwen2.5-Coder-32B : le meilleur juge mesuré par le banc {@code judge-finetune} — κ = 0,801
     * contre 0,349 pour Mistral-24B, et 0,97 de justesse moyenne sur les trois contrôles de
     * fidélité, exactement ceux que cette classe applique. La disjonction des familles avec le
     * générateur est assurée côté {@link RagAnswerer}, qui tourne sous {@code llama3.1}.
     * Raisonnement complet dans {@link RagContextJudge}.
     */
    private static final String DEFAULT_MODEL =
        "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit";

    private static final String SYSTEM_PROMPT =
        "Tu es un juge IA ultra-rigoureux. TÂCHE: RAG_FAITHFULNESS. "
        + "Analyse la situation pas à pas dans <thinking> avant de rendre ton verdict JSON.";

    /** Intitulés verbatim du corpus — toute variation sort le modèle de sa distribution. */
    private static final String CRITERES = """
        1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
        2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
        3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.""";

    public static final List<String> CONTROLES =
        List.of("affirmations_etayees", "absence_invention", "citations_exactes");

    /**
     * Les mêmes conventions que le juge de contexte, et la n° 4 les concerne directement :
     * elle fixe la portée de {@code citations_exactes} pour {@code RAG_FAITHFULNESS} — une
     * sortie inventée de bout en bout ne déforme aucune citation, le contrôle vaut vrai par
     * vacuité et le rejet est porté par les deux autres. Sans cette règle, deux juges peuvent
     * rendre FAIL pour des raisons opposées et l'accord s'effondre sans que rien ne le montre.
     */
    private static final String DEFAULT_SUFFIX = "judge-finetune/configs/conventions.md";

    private final ChatModel model;
    private final String modelLabel;
    private final String systemPrompt;

    private static String prop(String cle, String defaut) {
        String v = System.getProperty(cle);
        return (v == null || v.isBlank()) ? defaut : v.trim();
    }

    public RagAnswerJudge() {
        String provider = prop("jmh.answerjudge.provider", PROVIDER_OPENAI);
        boolean openai = PROVIDER_OPENAI.equalsIgnoreCase(provider);
        boolean schema = Boolean.parseBoolean(prop("jmh.answerjudge.schema", "false"));
        RagContextJudge.refuseSchemaSurMlx(schema, openai, "jmh.answerjudge.schema");
        String baseUrl = prop("jmh.answerjudge.url", openai ? DEFAULT_OPENAI_URL : DEFAULT_OLLAMA_URL);
        String modelName = prop("jmh.answerjudge.model", DEFAULT_MODEL);
        String adapter = prop("jmh.answerjudge.adapter", "");

        if (openai) {
            var builder = OpenAiChatModel.builder()
                .baseUrl(baseUrl).apiKey("none").modelName(modelName)
                .temperature(0.0).timeout(Duration.ofSeconds(180));
            if (!adapter.isBlank()) builder.customParameters(Map.of("adapters", adapter));
            this.model = builder.build();
        } else {
            var ollama = OllamaChatModel.builder()
                .baseUrl(baseUrl).modelName(modelName)
                .temperature(0.0).timeout(Duration.ofSeconds(180));
            if (schema) {
                // Divergence du 2026-10-18, déclarée dans PREENREGISTREMENT_SCHEMA.md :
                // qwen2.5-coder:32b refuse think() (« does not support thinking »).
                ollama.responseFormat(RagContextJudge.schemaDe("verdict_reponse", CONTROLES));
            }
            this.model = ollama.build();
        }
        String suffixe = RagContextJudge.chargeSuffixe(prop("jmh.answerjudge.suffix", DEFAULT_SUFFIX));
        this.systemPrompt = suffixe.isBlank() ? SYSTEM_PROMPT : SYSTEM_PROMPT + "\n\n" + suffixe;
        this.modelLabel = (adapter.isBlank() ? modelName : modelName + "+" + adapter)
            + (suffixe.isBlank() ? "" : "+conventions");
        logger.info("RagAnswerJudge initialisé : {} sur {} (provider={}, conventions={})",
            modelName, baseUrl, provider, suffixe.isBlank() ? "non" : "oui");
    }

    /** Injection directe, pour les tests. */
    public RagAnswerJudge(ChatModel model) {
        this.model = model;
        this.modelLabel = "injected";
        this.systemPrompt = SYSTEM_PROMPT;
    }

    public String getModelLabel() {
        return modelLabel;
    }

    /**
     * Juge la fidélité de la réponse au contexte qui l'a produite.
     *
     * @param contexteSoumis le contexte <b>exact</b> vu par le générateur, tel que rendu par
     *                       {@link RagAnswerer.Answer#contexte()}. Lui en donner un autre —
     *                       mélangé, retronqué — ferait sanctionner comme invention une phrase
     *                       puisée dans un extrait que le juge n'aurait pas reçu.
     * @param indices        indices FQN attendus, utilisés pour un recoupement déterministe
     *                       (couverture des indices dans la <b>réponse</b>, sans LLM)
     */
    public RagContextJudge.Judgement judge(String question, String contexteSoumis,
                                           String reponse, String[] indices) {
        if (reponse == null || reponse.isBlank()) {
            return new RagContextJudge.Judgement(Map.of(), "FAIL", "Aucune réponse générée", 0.0, true);
        }
        double couverture = RagContextJudge.computeHintCoverage(reponse, indices);

        String user = """
            ### CONTEXTE / RAG
            %s

            ### ENTREE / REQUÊTE
            %s

            ### SORTIE À ÉVALUER
            %s

            ### CRITÈRES DE VALIDATION
            %s""".formatted(contexteSoumis, question, reponse.strip(), CRITERES);

        try {
            ChatResponse response = model.chat(List.<ChatMessage>of(
                SystemMessage.from(systemPrompt), UserMessage.from(user)));
            var message = response.aiMessage();
            return RagContextJudge.parse(message == null ? "" : message.text(), couverture);
        } catch (Exception e) {
            logger.warn("Juge de réponse en échec sur '{}' : {}", question, e.getMessage());
            return new RagContextJudge.Judgement(
                Map.of(), RagContextJudge.INVALID, "Appel en échec : " + e.getMessage(), couverture, false);
        }
    }
}
