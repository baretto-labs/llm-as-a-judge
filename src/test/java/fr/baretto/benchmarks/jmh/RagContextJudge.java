package fr.baretto.benchmarks.jmh;

import dev.langchain4j.data.message.AiMessage;
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
 * {@code <thinking>} avant le JSON. L'analyse est donc tolérante, et reprend la règle déjà éprouvée
 * côté Python : <b>le dernier objet JSON du texte qui porte un {@code verdict}</b>.</p>
 *
 * <p><b>Correction du 2026-10-18.</b> Ce paragraphe affirmait que « la sortie structurée de
 * LangChain4j exige un JSON seul et échouerait ». <b>C'est faux</b>, et la phrase est retirée plutôt
 * que laissée : {@code OllamaChatRequest} porte {@code setFormat(Object)} <b>et</b>
 * {@code setThink(Boolean)}, et le builder expose {@code .responseFormat(...)}, {@code .think(true)}
 * et {@code .returnThinking(true)} — raisonnement et schéma sont orthogonaux. La contrainte réelle
 * était celle d'<b>un seul serveur</b> : {@code mlx_lm.server} 0.31.3 n'implémente pas
 * {@code response_format} (aucune occurrence dans {@code server.py}, aucun décodage sous grammaire)
 * et <b>ignore le champ en silence</b>. L'arbitrage restait donc bon pour la voie MLX ; sa
 * justification était trop générale.</p>
 *
 * <p>Depuis, {@code -Djmh.judge.schema=true} contraint le décodage sur la voie Ollama — schéma gelé
 * par {@code benchmarks/PREENREGISTREMENT_SCHEMA.md}, et refus explicite sur la voie MLX plutôt
 * qu'un run qui se croirait contraint. Inactif par défaut : les chiffres publiés restent lisibles
 * tels quels.</p>
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
    // Port 8083 : celui de 32B-baseline-conventions dans judge-finetune/configs/variants.json.
    private static final String DEFAULT_OPENAI_URL = "http://127.0.0.1:8083/v1";
    private static final String DEFAULT_OLLAMA_URL = "http://localhost:11434";

    /**
     * Qwen2.5-Coder-32B depuis le 2026-10-17, en remplacement de Qwen2.5-Coder-14B.
     *
     * <p><b>Choisi sur une mesure, pas sur une famille.</b> Le premier choix de la journée avait
     * été Mistral-24B, au motif qu'un juge de la famille du générateur surnote. Le banc
     * {@code judge-finetune} a rendu ses chiffres le soir même, sur les 50 items de l'étalon :
     * Mistral-24B accorde κ = 0,349 et 64 % de justesse, le 32B κ = 0,801 et 90 %. Le biais
     * d'auto-préférence est un risque ; un juge deux fois moins d'accord avec l'étalon est un
     * défaut déjà constaté. On prend le meilleur juge mesuré.</p>
     *
     * <p><b>La disjonction des familles est préservée ailleurs</b> : {@link RagAnswerer} génère
     * sous {@code llama3.1} et non sous Qwen. Juge et générateur restent de familles différentes,
     * et c'est le générateur qui a bougé — lui est une constante identique sur les trois bras,
     * le juge se choisit sur son accord mesuré.</p>
     *
     * <p>18,4 Go en 4 bits, déjà en cache local, une variante servie à la fois.</p>
     */
    private static final String DEFAULT_MODEL =
        "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit";

    /**
     * Adaptateur LoRA à appliquer, transmis dans le corps de chaque requête.
     *
     * <p><b>Le {@code --adapter-path} passé au démarrage de mlx_lm.server ne suffit pas</b>, et
     * l'échec est silencieux : le serveur l'enregistre sous la clé littérale {@code default_model}
     * ({@code server.py:316}) et ne l'applique que si la requête demande ce nom-là. Toute requête
     * nommant un vrai modèle reçoit les poids de base, sans le moindre avertissement — vérifié le
     * 2026-09-21, le juge rendait alors un JSON au mauvais schéma et chaque jugement aurait compté
     * INVALID. Le champ {@code adapters} du corps, lui, fonctionne.</p>
     *
     * <p><b>Chemin résolu par le serveur, pas par la JVM.</b> Il est relatif au répertoire d'où
     * {@code mlx_lm.server} a été lancé — {@code judge-finetune/} — et non à la racine du dépôt
     * d'où Maven s'exécute.</p>
     *
     * <p>{@code -Djmh.judge.adapter=} (vide) interroge le modèle de base.</p>
     *
     * <p><b>Vide par défaut depuis le 2026-10-17, et c'est une correction.</b> Le défaut était
     * {@code adapters/14b-judge-ckpt200}, c'est-à-dire le juge <i>fine-tuné</i> — celui que le
     * banc de {@code judge-finetune/} a mesuré <b>moins bon</b> que les simples conventions :
     * accord κ 0,44 contre 0,48, stabilité 58 % contre 76 %, à justesse égale (76 %). La
     * campagne du 2026-09-24 a donc été jugée par la pire des variantes disponibles. Ce qui
     * achète l'accord, ce sont les conventions ({@code jmh.judge.suffix}), pas l'entraînement.
     * De surcroît cet adaptateur a été entraîné sur le 14B : ses poids n'ont pas les dimensions
     * du 32B désormais servi, et le serveur refuserait de les charger.</p>
     */
    private static final String DEFAULT_ADAPTER = "";

    /**
     * Conventions de notation ajoutées au message système, chemin relatif à la racine du dépôt.
     *
     * <p>C'est le levier que le banc de {@code judge-finetune/} a mesuré comme décisif :
     * invite nue κ = 0,00, + quatre conventions κ = 0,48. Trois des quatre sont invisibles
     * depuis l'invite seule — préférence non bloquante, portée de {@code citations_exactes},
     * règle PASS ⟺ tous les contrôles vrais. S'en passer, c'est laisser le juge improviser
     * trois arbitrages que l'étude a déjà tranchés.</p>
     *
     * <p>{@code -Djmh.judge.suffix=} (vide) retrouve le juge sans conventions.</p>
     */
    private static final String DEFAULT_SUFFIX = "judge-finetune/configs/conventions.md";

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
    private final String systemPrompt;

    /**
     * Propriété système, une valeur vide comptant comme absente.
     *
     * <p>{@code System.getProperty(cle, defaut)} ne rend le défaut que si la propriété est
     * <b>null</b>. Or surefire les transmet toutes, y compris non renseignées, donc elles
     * arrivent comme chaîne vide et le défaut n'est jamais appliqué. Sans ce garde,
     * {@code jmh.judge.adapter} vaudrait {@code ""}, aucun adaptateur ne serait envoyé, et le
     * juge interrogerait le <b>modèle de base</b> en se croyant fine-tuné — silencieusement.</p>
     */
    private static String prop(String cle, String defaut) {
        String v = System.getProperty(cle);
        return (v == null || v.isBlank()) ? defaut : v.trim();
    }


    /**
     * Schéma gelé par {@code benchmarks/PREENREGISTREMENT_SCHEMA.md}, partagé par les deux juges.
     *
     * <p>{@code checks} vient <b>avant</b> {@code verdict}, comme dans le corpus : le modèle génère
     * de gauche à droite et doit poser les faits avant de trancher. Les trois contrôles sont
     * requis, {@code additionalProperties} est interdit — un contrôle manquant devient impossible,
     * et c'est précisément la classe d'échec que ce juge est là pour supprimer.</p>
     *
     * <p>Aucun champ {@code thinking} : Ollama rend le raisonnement dans son propre champ. Si un
     * serveur ne le rendait pas, ce serait une divergence à déclarer, pas à rattraper ici.</p>
     */
    static ResponseFormat schemaDe(String nom, List<String> controles) {
        var checks = JsonObjectSchema.builder().additionalProperties(false);
        for (String c : controles) {
            checks.addProperty(c, JsonBooleanSchema.builder().build());
        }
        checks.required(controles);
        return ResponseFormat.builder()
            .type(ResponseFormatType.JSON)
            .jsonSchema(JsonSchema.builder()
                .name(nom)
                .rootElement(JsonObjectSchema.builder()
                    .addProperty("checks", checks.build())
                    .addProperty("verdict", JsonEnumSchema.builder()
                        .enumValues(List.of("PASS", "FAIL")).build())
                    .addProperty("reason", JsonStringSchema.builder().build())
                    .required(List.of("checks", "verdict", "reason"))
                    .additionalProperties(false)
                    .build())
                .build())
            .build();
    }

    /**
     * {@code mlx_lm.server} 0.31.3 <b>ignore {@code response_format} en silence</b> : aucune
     * occurrence dans {@code server.py}, aucun décodage sous grammaire. Laisser passer le drapeau
     * sur cette voie produirait un run qui se croit contraint et ne l'est pas — exactement le genre
     * de mesure muette que ce dépôt refuse. On échoue donc fort, et tôt.
     */
    static void refuseSchemaSurMlx(boolean schema, boolean openai, String propriete) {
        if (schema && openai) {
            throw new IllegalStateException(
                propriete + "=true exige le provider ollama : mlx_lm.server ignore response_format "
                + "en silence, le jugement ne serait pas contraint. "
                + "Relance avec -Djmh.judge.provider=ollama (et -Djmh.answerjudge.provider=ollama).");
        }
    }

    public RagContextJudge() {
        String provider = prop("jmh.judge.provider", PROVIDER_OPENAI);
        boolean openai = PROVIDER_OPENAI.equalsIgnoreCase(provider);
        boolean schema = Boolean.parseBoolean(prop("jmh.judge.schema", "false"));
        refuseSchemaSurMlx(schema, openai, "jmh.judge.schema");
        String baseUrl = prop("jmh.judge.url", openai ? DEFAULT_OPENAI_URL : DEFAULT_OLLAMA_URL);
        String modelName = prop("jmh.judge.model", DEFAULT_MODEL);
        String adapter = prop("jmh.judge.adapter", DEFAULT_ADAPTER);

        if (openai) {
            var builder = OpenAiChatModel.builder()
                .baseUrl(baseUrl).apiKey("none").modelName(modelName)
                .temperature(0.0).timeout(Duration.ofSeconds(120));
            if (!adapter.isBlank()) {
                builder.customParameters(Map.of("adapters", adapter));
            }
            this.model = builder.build();
        } else {
            var ollama = OllamaChatModel.builder()
                .baseUrl(baseUrl).modelName(modelName)
                .temperature(0.0).timeout(Duration.ofSeconds(120));
            if (schema) {
                // Divergence du 2026-10-18, déclarée dans PREENREGISTREMENT_SCHEMA.md : le
                // dispositif gelé prévoyait think(true), mais qwen2.5-coder:32b le refuse
                // (« does not support thinking »). Le pré-enregistrement fixait la conduite —
                // déclarer la divergence, surtout pas ajouter un champ thinking au schéma.
                ollama.responseFormat(schemaDe("verdict_contexte", CONTROLES));
            }
            this.model = ollama.build();
        }
        String suffixe = chargeSuffixe(prop("jmh.judge.suffix", DEFAULT_SUFFIX));
        this.systemPrompt = suffixe.isBlank() ? SYSTEM_PROMPT : SYSTEM_PROMPT + "\n\n" + suffixe;
        this.modelLabel = (adapter.isBlank() ? modelName : modelName + "+" + adapter)
            + (suffixe.isBlank() ? "" : "+conventions");
        logger.info("RagContextJudge initialisé : {} sur {} (provider={}, adaptateur={}, conventions={})",
            modelName, baseUrl, provider, adapter.isBlank() ? "aucun" : adapter,
            suffixe.isBlank() ? "non" : suffixe.length() + " caractères");
    }

    /**
     * Échec franc si le fichier est introuvable, jamais un repli silencieux : un juge privé de
     * ses conventions rendrait des verdicts d'une autre variante que celle inscrite dans le
     * JSONL, et le libellé du modèle mentirait.
     */
    static String chargeSuffixe(String chemin) {
        if (chemin == null || chemin.isBlank()) return "";
        java.nio.file.Path p = java.nio.file.Path.of(chemin);
        if (!java.nio.file.Files.isRegularFile(p)) {
            throw new IllegalStateException("suffixe système introuvable : " + p.toAbsolutePath()
                + " — le chemin est relatif à la racine du dépôt, d'où Maven s'exécute.");
        }
        try {
            return java.nio.file.Files.readString(p).strip();
        } catch (java.io.IOException e) {
            throw new IllegalStateException("suffixe système illisible : " + p, e);
        }
    }

    /** Injection directe, pour les tests. */
    public RagContextJudge(ChatModel model) {
        this.model = model;
        this.modelLabel = "injected";
        this.systemPrompt = SYSTEM_PROMPT;
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

        // Mélange GRAÎNÉ PAR LA QUESTION, et non aléatoire.
        //
        // La version non graînée rendait la mesure irreproductible, constaté le 2026-09-24 en
        // comparant deux runs : `hintCoverage` — fonction pure du contexte et des indices —
        // différait sur 21 questions sur 60 alors que la récupération était identique au bit près.
        // La cause était l'interaction du mélange avec la troncature à 6000 caractères, qui
        // intervient APRÈS : selon le tirage, ce ne sont pas les mêmes extraits qui survivent,
        // donc ni la même invite ni le même verdict.
        //
        // La graine dérive du texte de la question : l'ordre reste brassé — le biais de position
        // est toujours atténué — mais il est identique d'un run à l'autre ET identique pour les
        // deux stratégies sur une même question, ce qui est indispensable à un test apparié.
        List<String> shuffled = new ArrayList<>(retrievedContext);
        Collections.shuffle(shuffled, new java.util.Random(question.hashCode()));
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
                SystemMessage.from(systemPrompt), UserMessage.from(user)));
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
