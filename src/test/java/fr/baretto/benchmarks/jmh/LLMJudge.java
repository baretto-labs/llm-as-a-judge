package fr.baretto.benchmarks.jmh;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.ollama.OllamaChatModel;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Juge LLM pour évaluer la pertinence du contexte retourné par une stratégie RAG.
 *
 * <p>Supporte plusieurs modèles juges en parallèle (ensemble) via la propriété système
 * {@code jmh.judge.models} (liste séparée par virgules). Le score final est la moyenne
 * des scores de chaque juge.</p>
 *
 * <p>Configuration via propriétés système :</p>
 * <pre>
 *   -Djmh.judge.models=qwen2.5:14b,mistral:32b   (liste — recommandé)
 *   -Djmh.judge.model=qwen2.5:14b                (modèle unique — rétrocompatible)
 *   -Djmh.judge.url=http://localhost:11434        (optionnel)
 * </pre>
 *
 * <p>Fonctionnalités :</p>
 * <ul>
 *   <li>Structured output via LangChain4j AiServices — aucun regex</li>
 *   <li>Few-shot examples dans le prompt pour ancrer l'échelle (P2.1)</li>
 *   <li>Position bias mitigation : ordre des chunks mélangé aléatoirement (P2.3)</li>
 *   <li>Multi-juge avec moyenne des scores (P2.2)</li>
 * </ul>
 *
 * <p>Métriques retournées par {@link JudgementResult} :</p>
 * <ul>
 *   <li>{@code score} — pertinence 0-10 (int, moyenne des juges)</li>
 *   <li>{@code rationale} — explication en une phrase</li>
 *   <li>{@code suggestsUnknown} — true si le contexte forcerait un "I don't know"</li>
 *   <li>{@code hintCoverage} — fraction des expectedFqnHints trouvés (calcul programmatique)</li>
 * </ul>
 */
public class LLMJudge {

    private static final Logger logger = LoggerFactory.getLogger(LLMJudge.class);

    private static final String DEFAULT_JUDGE_MODEL = "qwen2.5:14b";
    private static final String DEFAULT_OLLAMA_URL  = "http://localhost:11434";

    // ── Structured output ──────────────────────────────────────────────────

    /**
     * Résultat structuré retourné par le modèle LLM.
     * LangChain4j AiServices sérialise automatiquement en JSON et désérialise avec Jackson.
     * Le schéma JSON est inféré depuis les noms de champs — aucun regex nécessaire.
     */
    public record JudgementOutput(
        int     score,           // entier 0-10, garanti par le schéma JSON
        String  rationale,       // une phrase expliquant le score
        boolean suggestsUnknown  // vrai si le contexte est insuffisant pour répondre
    ) {}

    /**
     * Interface AiService — LangChain4j génère un proxy qui :
     * 1. Envoie le SystemMessage + UserMessage au modèle
     * 2. Force le mode JSON (schema enforcement côté Ollama)
     * 3. Désérialise la réponse en {@link JudgementOutput} via Jackson
     *
     * <p>Le prompt inclut 3 exemples annotés (few-shot) pour ancrer l'échelle,
     * conformément aux standards MT-Bench / Chatbot Arena 2026.</p>
     */
    interface JudgeService {
        @SystemMessage("""
            You are an expert Java software engineer evaluating a RAG (Retrieval-Augmented Generation) system.
            Your task: assess whether the retrieved context contains enough information to accurately answer the question.

            Scoring scale (integer 0 to 10):
            - 10 : context fully and directly answers the question
            - 7-9 : context mostly answers with minor gaps
            - 4-6 : context partially answers, key information is missing
            - 1-3 : context is tangentially related but does not answer
            - 0   : context is irrelevant or empty

            Also determine if the context would force the system to answer "I don't know".

            --- FEW-SHOT EXAMPLES ---

            Example 1 (score 9):
            Question: What fields does Class0Service have?
            Context: Type: com.example.service.Class0Service
            Field: private String id;
            Field: private List<String> items;
            Field: private int counter;
            Method: public String getId()
            Method: public void processInput(String input)
            Expected output: {"score": 9, "rationale": "Context directly lists all three fields (id, items, counter) of Class0Service with their types.", "suggestsUnknown": false}

            Example 2 (score 4):
            Question: What is the call chain starting from Class0Service?
            Context: Type: com.example.service.Class0Service
            Field: private String id;
            Method: public void processInput(String input)
            Expected output: {"score": 4, "rationale": "Context shows Class0Service but lacks the delegation chain to subsequent classes, making the full call chain unanswerable.", "suggestsUnknown": false}

            Example 3 (score 0):
            Question: Which classes in com.example.repository call classes in com.example.service?
            Context: Type: java.util.ArrayList
            Method: boolean add(Object element)
            Method: Object get(int index)
            Expected output: {"score": 0, "rationale": "Context contains only java.util standard library classes, completely unrelated to the question about repository/service interactions.", "suggestsUnknown": true}

            --- END EXAMPLES ---

            Be strict and consistent. Respond with the structured output only.
            """)
        JudgementOutput evaluate(@UserMessage String userPrompt);
    }

    // ── Fields ────────────────────────────────────────────────────────────

    private final List<JudgeService> judgeServices;
    private final String modelNamesLabel;

    /**
     * Crée un juge avec le(s) modèle(s) configuré(s) via propriété système.
     * {@code jmh.judge.models} prend la priorité sur {@code jmh.judge.model}.
     */
    public LLMJudge() {
        String modelsProperty = System.getProperty("jmh.judge.models",
            System.getProperty("jmh.judge.model", DEFAULT_JUDGE_MODEL));
        String baseUrl = System.getProperty("jmh.judge.url", DEFAULT_OLLAMA_URL);

        List<String> modelNames = Arrays.stream(modelsProperty.split(","))
            .map(String::trim)
            .filter(s -> !s.isEmpty())
            .toList();

        this.modelNamesLabel = String.join(",", modelNames);
        this.judgeServices = modelNames.stream()
            .map(name -> createJudgeService(name, baseUrl))
            .toList();

        logger.info("LLMJudge initialisé avec {} juge(s): [{}] sur {}",
            judgeServices.size(), modelNamesLabel, baseUrl);
    }

    /** Constructeur pour injection directe (tests). */
    public LLMJudge(ChatModel chatModel) {
        this.judgeServices = List.of(AiServices.create(JudgeService.class, chatModel));
        this.modelNamesLabel = "injected";
    }

    /** @return Label des modèles juges utilisés (pour les fichiers JSONL). */
    public String getModelNamesLabel() {
        return modelNamesLabel;
    }

    // ── Public API ────────────────────────────────────────────────────────

    /**
     * Évalue la pertinence du contexte retourné pour répondre à la question.
     *
     * <p>L'ordre des chunks est mélangé aléatoirement avant évaluation pour mitiger
     * le position bias (lost-in-the-middle). Si plusieurs juges sont configurés,
     * les scores sont moyennés et la rationale du premier juge est conservée.</p>
     *
     * @param question         Question posée à la stratégie RAG
     * @param retrievedContext Contexte retourné par la stratégie (liste de chunks)
     * @param expectedHints    Fragments FQN attendus dans le contexte
     * @return Résultat du jugement avec score, rationale, suggestsUnknown, hintCoverage
     */
    public JudgementResult judge(String question, List<String> retrievedContext, String[] expectedHints) {
        if (retrievedContext.isEmpty()) {
            return new JudgementResult(0, "No context retrieved", true, 0.0);
        }

        // Position bias mitigation (P2.3) : mélanger l'ordre des chunks
        List<String> shuffledContext = new ArrayList<>(retrievedContext);
        Collections.shuffle(shuffledContext);

        String contextText = String.join("\n---\n", shuffledContext);
        // Tronquer à ~6000 caractères pour rester dans le context window du juge
        if (contextText.length() > 6000) {
            contextText = contextText.substring(0, 6000) + "\n[... truncated ...]";
        }

        // hintCoverage calculé après troncature — cohérent avec ce que le juge voit réellement
        // Calcul programmatique (déterministe) : on ne demande pas au LLM quels hints il a trouvés
        // pour éviter les hallucinations du type "j'ai vu X" alors que X n'y est pas.
        double hintCoverage = computeHintCoverage(contextText, expectedHints);

        String userPrompt = "Question: %s\n\nRetrieved context:\n%s".formatted(question, contextText);

        // Multi-juge (P2.2) : exécuter tous les juges et moyenner les scores
        List<JudgementOutput> outputs = new ArrayList<>();
        for (JudgeService svc : judgeServices) {
            try {
                JudgementOutput output = svc.evaluate(userPrompt);
                outputs.add(output);
                logger.debug("Judge output: score={}, rationale='{}'", output.score(), output.rationale());
            } catch (Exception e) {
                logger.warn("LLM judge failed for question '{}': {}", question, e.getMessage());
            }
        }

        if (outputs.isEmpty()) {
            return new JudgementResult(-1, "All judges failed", false, hintCoverage);
        }

        int avgScore = (int) Math.round(
            outputs.stream()
                .mapToInt(o -> Math.max(0, Math.min(10, o.score())))
                .average()
                .orElse(-1)
        );
        boolean suggestsUnknown = outputs.stream().anyMatch(JudgementOutput::suggestsUnknown);
        String rationale = outputs.size() == 1
            ? outputs.get(0).rationale()
            : "[avg %d judges] %s".formatted(outputs.size(), outputs.get(0).rationale());

        logger.debug("Final score={} ({} judges), suggestsUnknown={}", avgScore, outputs.size(), suggestsUnknown);
        return new JudgementResult(avgScore, rationale, suggestsUnknown, hintCoverage);
    }

    // ── Private helpers ───────────────────────────────────────────────────

    private JudgeService createJudgeService(String modelName, String baseUrl) {
        ChatModel chatModel = OllamaChatModel.builder()
            .baseUrl(baseUrl)
            .modelName(modelName)
            .temperature(0.0)
            .timeout(Duration.ofSeconds(120))
            .build();
        return AiServices.create(JudgeService.class, chatModel);
    }

    /**
     * Calcule la fraction des hints attendus présents dans le contexte (case-insensitive).
     * Opération déterministe sur le contexte tronqué — pas de LLM impliqué.
     */
    private double computeHintCoverage(String contextText, String[] hints) {
        if (hints == null || hints.length == 0) return 1.0;
        String lower = contextText.toLowerCase();
        long found = 0;
        for (String hint : hints) {
            if (lower.contains(hint.toLowerCase())) found++;
        }
        return (double) found / hints.length;
    }

    // ── Result type ───────────────────────────────────────────────────────

    /**
     * Résultat complet d'un jugement.
     *
     * @param score           Score de pertinence 0-10 (-1 si erreur du juge)
     * @param rationale       Explication du score (une phrase)
     * @param suggestsUnknown Le contexte forcerait-il un "I don't know" ?
     * @param hintCoverage    Fraction des FQN hints trouvés dans le contexte (0.0–1.0)
     */
    public record JudgementResult(
        int    score,
        String rationale,
        boolean suggestsUnknown,
        double hintCoverage
    ) {}
}
