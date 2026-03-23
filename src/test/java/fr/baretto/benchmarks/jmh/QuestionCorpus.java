package fr.baretto.benchmarks.jmh;

import java.util.List;

/**
 * Corpus de questions basé sur la vraie codebase OllamAssist.
 *
 * <ul>
 *   <li><b>LOCAL</b> — question sur une seule classe ou méthode précise</li>
 *   <li><b>STRUCTURAL</b> — question sur l'héritage, les interfaces, les relations directes</li>
 *   <li><b>CROSS_MODULE</b> — question traversant plusieurs packages/modules</li>
 * </ul>
 *
 * Les {@code expectedFqnHints} sont des fragments de FQN ou de nom attendus dans le
 * contexte retourné (case-insensitive). Permettent une mesure déterministe en complément
 * du scoring LLM-as-a-judge.
 */
public class QuestionCorpus {

    public enum Difficulty { LOCAL, STRUCTURAL, CROSS_MODULE }

    public record Question(String text, Difficulty difficulty, String[] expectedFqnHints) {}

    public static final List<Question> QUESTIONS = List.of(

        // ── LOCAL : une seule entité ciblée (10 questions) ───────────────────

        new Question(
            "What does the retrieve method do in ContextRetriever?",
            Difficulty.LOCAL,
            new String[]{"ContextRetriever", "retrieve", "Content"}
        ),
        new Question(
            "What does the calculateDynamicThreshold method compute in LuceneEmbeddingStore?",
            Difficulty.LOCAL,
            new String[]{"LuceneEmbeddingStore", "calculateDynamicThreshold", "scores"}
        ),
        new Question(
            "How does DocumentIndexingPipeline handle document errors and retries?",
            Difficulty.LOCAL,
            new String[]{"DocumentIndexingPipeline", "handleDocumentError", "MAX_RETRIES"}
        ),
        new Question(
            "What does BracketCallParser parse from LLM output?",
            Difficulty.LOCAL,
            new String[]{"BracketCallParser", "parse", "CALL"}
        ),
        new Question(
            "How does EnhancedCompletionService clean up raw LLM suggestions?",
            Difficulty.LOCAL,
            new String[]{"EnhancedCompletionService", "processSuggestion", "removeCodeBlockMarkers"}
        ),
        new Question(
            "What authentication header does AuthenticationHelper generate?",
            Difficulty.LOCAL,
            new String[]{"AuthenticationHelper", "createBasicAuthHeader", "Base64"}
        ),
        new Question(
            "How does SuggestionCache generate cache keys for completion requests?",
            Difficulty.LOCAL,
            new String[]{"SuggestionCache", "generateCacheKey"}
        ),
        new Question(
            "What constants does DocumentIndexingPipeline define for batch processing?",
            Difficulty.LOCAL,
            new String[]{"DocumentIndexingPipeline", "BATCH_SIZE", "MAX_RETRIES", "SYNCHRONOUS_BATCH_SIZE"}
        ),
        new Question(
            "What does the dismiss method do in RefactorAction?",
            Difficulty.LOCAL,
            new String[]{"RefactorAction", "dismiss"}
        ),
        new Question(
            "How does PrerequisiteService check if the local embedding model is available?",
            Difficulty.LOCAL,
            new String[]{"PrerequisiteService", "checkLocalEmbeddingModel", "DJL"}
        ),

        // ── STRUCTURAL : héritage et relations directes (10 questions) ───────

        new Question(
            "What interfaces does OllamaService implement?",
            Difficulty.STRUCTURAL,
            new String[]{"OllamaService", "Disposable", "ModelListener"}
        ),
        new Question(
            "Which class extends GutterIconRenderer in OllamAssist?",
            Difficulty.STRUCTURAL,
            new String[]{"OllamaGutterIconRenderer", "GutterIconRenderer"}
        ),
        new Question(
            "What methods does the Assistant interface define?",
            Difficulty.STRUCTURAL,
            new String[]{"Assistant", "chat", "refactor", "TokenStream"}
        ),
        new Question(
            "What does LuceneEmbeddingStore implement?",
            Difficulty.STRUCTURAL,
            new String[]{"LuceneEmbeddingStore", "EmbeddingStore", "Closeable", "Disposable"}
        ),
        new Question(
            "Which classes implement the ToolCallParser interface?",
            Difficulty.STRUCTURAL,
            new String[]{"BracketCallParser", "ToolCallParser"}
        ),
        new Question(
            "What does DocumentIndexingPipeline implement?",
            Difficulty.STRUCTURAL,
            new String[]{"DocumentIndexingPipeline", "AutoCloseable"}
        ),
        new Question(
            "Which settings classes implement PersistentStateComponent?",
            Difficulty.STRUCTURAL,
            new String[]{"OllamaSettings", "RAGSettings", "ActionsSettings", "PersistentStateComponent"}
        ),
        new Question(
            "What does OllamAssistStartup implement and what is its role?",
            Difficulty.STRUCTURAL,
            new String[]{"OllamAssistStartup", "ProjectActivity", "execute"}
        ),
        new Question(
            "What class extends AnAction for the refactoring feature?",
            Difficulty.STRUCTURAL,
            new String[]{"RefactorAction", "AnAction"}
        ),
        new Question(
            "What interface does ContextRetriever implement and what does it override?",
            Difficulty.STRUCTURAL,
            new String[]{"ContextRetriever", "ContentRetriever", "retrieve"}
        ),

        // ── CROSS_MODULE : traversée multi-packages (10 questions) ───────────

        new Question(
            "How does OllamAssistStartup initialize EditorListener on project load?",
            Difficulty.CROSS_MODULE,
            new String[]{"OllamAssistStartup", "EditorListener", "execute"}
        ),
        new Question(
            "How does FileCreator request user approval via FileApprovalNotifier?",
            Difficulty.CROSS_MODULE,
            new String[]{"FileCreator", "FileApprovalNotifier", "requestApproval"}
        ),
        new Question(
            "How does EnhancedCompletionService use OptimizedLightModelAssistant to generate suggestions?",
            Difficulty.CROSS_MODULE,
            new String[]{"EnhancedCompletionService", "OptimizedLightModelAssistant", "completeAsync"}
        ),
        new Question(
            "How does DocumentIndexingPipeline interact with LuceneEmbeddingStore to persist documents?",
            Difficulty.CROSS_MODULE,
            new String[]{"DocumentIndexingPipeline", "LuceneEmbeddingStore"}
        ),
        new Question(
            "How does ContextRetriever combine results from WorkspaceContextRetriever and DuckDuckGoContentRetriever?",
            Difficulty.CROSS_MODULE,
            new String[]{"ContextRetriever", "WorkspaceContextRetriever", "DuckDuckGoContentRetriever"}
        ),
        new Question(
            "How does OllamaService initialize LuceneEmbeddingStore and DocumentIndexingPipeline together?",
            Difficulty.CROSS_MODULE,
            new String[]{"OllamaService", "LuceneEmbeddingStore", "DocumentIndexingPipeline", "init"}
        ),
        new Question(
            "How does AskFromCodeAction notify the chat UI via NewUserMessageNotifier?",
            Difficulty.CROSS_MODULE,
            new String[]{"AskFromCodeAction", "NewUserMessageNotifier"}
        ),
        new Question(
            "How does PrerequisiteService fall back from local DJL embedding to Ollama?",
            Difficulty.CROSS_MODULE,
            new String[]{"PrerequisiteService", "checkEmbeddingModelAsync", "localFailedWithFallback"}
        ),
        new Question(
            "How does SelectionGutterIcon trigger OverlayPromptPanelFactory when the icon is clicked?",
            Difficulty.CROSS_MODULE,
            new String[]{"SelectionGutterIcon", "OverlayPromptPanelFactory", "OllamaGutterIconRenderer"}
        ),
        new Question(
            "How does DocumentIngestFactory create the embedding model with DJL fallback to Ollama?",
            Difficulty.CROSS_MODULE,
            new String[]{"DocumentIngestFactory", "createEmbeddingModel", "BgeSmallEnV15Quantized", "OllamaEmbeddingModel"}
        )
    );

    private QuestionCorpus() {}
}
