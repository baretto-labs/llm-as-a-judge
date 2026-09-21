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

        // ── LOCAL : une seule entité ciblée (20 questions) ───────────────────

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
            // `createBasicAuthHeader` n'existe pas dans la codebase : indice inventé,
            // repéré le 2026-09-21 par scripts/verify_question_hints.py. Le hintCoverage
            // de cette question plafonnait donc à 2/3 sans que rien ne le signale.
            new String[]{"AuthenticationHelper", "buildAuthorizationHeaderValue", "AUTHORIZATION_HEADER"}
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

        new Question(
            "How does RRFFusion combine two ranked result lists into one?",
            Difficulty.LOCAL,
            new String[]{"RRFFusion", "fuse", "RRF_K"}
        ),
        new Question(
            "How does HybridRetriever run the KNN and BM25 searches?",
            Difficulty.LOCAL,
            new String[]{"HybridRetriever", "retrieve", "RRFFusion"}
        ),
        new Question(
            "How does CodeAwareDocumentSplitter split Java files compared to other files?",
            Difficulty.LOCAL,
            new String[]{"CodeAwareDocumentSplitter", "split", "fallbackSplit"}
        ),
        new Question(
            "What does SecretDetector return, and how can a line be excluded from detection?",
            Difficulty.LOCAL,
            new String[]{"SecretDetector", "detect", "ollamassist-nocheck"}
        ),
        new Question(
            "What transformations does PromptSanitizer apply to tool output?",
            Difficulty.LOCAL,
            new String[]{"PromptSanitizer", "sanitize", "sanitizeGoal"}
        ),
        new Question(
            "How does FilePathGuard prevent a write from escaping the project root?",
            Difficulty.LOCAL,
            new String[]{"FilePathGuard", "resolveConfined", "PathTraversalException"}
        ),
        new Question(
            "What operations does MyersDiff produce when comparing two lists of lines?",
            Difficulty.LOCAL,
            new String[]{"MyersDiff", "computeDiff", "computeCompactDiff"}
        ),
        new Question(
            "How does ModelSizeParser extract a parameter count from a model name?",
            Difficulty.LOCAL,
            new String[]{"ModelSizeParser", "extractParamCountBillions"}
        ),
        new Question(
            "How does AgentMemoryService bound the history it keeps?",
            Difficulty.LOCAL,
            new String[]{"AgentMemoryService", "MAX_RECORDS", "TTL_DAYS"}
        ),
        new Question(
            "What does UrlHelper do to a user-supplied Ollama URL before it is used?",
            Difficulty.LOCAL,
            new String[]{"UrlHelper", "normalizeUrl", "buildApiUrl"}
        ),

        // ── STRUCTURAL : héritage et relations directes (20 questions) ───────

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

        new Question(
            "Which classes implement the AgentTool interface?",
            Difficulty.STRUCTURAL,
            new String[]{"AgentTool", "ReadFileTool", "WriteFileTool", "SearchCodeTool"}
        ),
        new Question(
            "Which classes implement ContentRetriever in OllamAssist?",
            Difficulty.STRUCTURAL,
            new String[]{"ContentRetriever", "ContextRetriever", "HybridRetriever"}
        ),
        new Question(
            "Which renderers implement EditorCustomElementRenderer?",
            Difficulty.STRUCTURAL,
            new String[]{"EditorCustomElementRenderer", "InlayRenderer", "MultiSuggestionRenderer", "RefactoringInlayRenderer"}
        ),
        new Question(
            "What does ProjectFileListener implement?",
            Difficulty.STRUCTURAL,
            new String[]{"ProjectFileListener", "StoreNotifier", "Disposable"}
        ),
        new Question(
            "Which class implements NotificationStorage, and how is its state persisted?",
            Difficulty.STRUCTURAL,
            new String[]{"PersistentNotificationStorage", "NotificationStorage", "PersistentStateComponent"}
        ),
        new Question(
            "Which exception does FilePathGuard throw, and what does it extend?",
            Difficulty.STRUCTURAL,
            new String[]{"PathTraversalException", "SecurityException", "FilePathGuard"}
        ),
        new Question(
            "What does CorruptedIndexException extend, and where is it raised?",
            Difficulty.STRUCTURAL,
            new String[]{"CorruptedIndexException", "RuntimeException"}
        ),
        new Question(
            "Which settings panels extend JBPanel?",
            Difficulty.STRUCTURAL,
            new String[]{"RAGConfigPanel", "OllamaConfigPanel", "AgentConfigPanel", "JBPanel"}
        ),
        new Question(
            "Which classes implement ProjectActivity in OllamAssist?",
            Difficulty.STRUCTURAL,
            new String[]{"ProjectActivity", "OllamAssistStartup", "NotificationApplicationStartup"}
        ),
        new Question(
            "What do IdStartWithFilter and ShouldBeIndexed implement?",
            Difficulty.STRUCTURAL,
            new String[]{"IdStartWithFilter", "ShouldBeIndexed", "PathMatcher"}
        ),

        // ── CROSS_MODULE : traversée multi-packages (20 questions) ───────────

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
        ),
        new Question(
            "How does WriteFileTool check content for secrets before writing to disk?",
            Difficulty.CROSS_MODULE,
            new String[]{"WriteFileTool", "SecretDetector", "detect"}
        ),
        new Question(
            "How does DeleteFileTool obtain user approval before deleting a file?",
            Difficulty.CROSS_MODULE,
            new String[]{"DeleteFileTool", "ToolApprovalHelper", "requestApproval"}
        ),
        new Question(
            "How does ToolApprovalHelper wait for an approval decision?",
            Difficulty.CROSS_MODULE,
            new String[]{"ToolApprovalHelper", "FileApprovalNotifier", "ApprovalDecision"}
        ),
        new Question(
            "How does RAGConfigPanel trigger a full reindexation of the project?",
            Difficulty.CROSS_MODULE,
            new String[]{"RAGConfigPanel", "StoreNotifier", "ProjectFileListener", "clearDatabaseAndRunIndexation"}
        ),
        new Question(
            "How does CommitMessageGenerator produce a commit message from a diff?",
            Difficulty.CROSS_MODULE,
            new String[]{"CommitMessageGenerator", "LightModelAssistant", "MessageCleaner"}
        ),
        new Question(
            "How does DocumentIngestFactory authenticate its requests to Ollama?",
            Difficulty.CROSS_MODULE,
            new String[]{"DocumentIngestFactory", "AuthenticationHelper", "authHeaders"}
        ),
        new Question(
            "How does AddToContextAction add a selected file to the workspace context?",
            Difficulty.CROSS_MODULE,
            new String[]{"AddToContextAction", "WorkspaceContextRetriever", "addFile"}
        ),
        new Question(
            "How does OllamaContent obtain the RAG sources used for the last answer?",
            Difficulty.CROSS_MODULE,
            new String[]{"OllamaContent", "ContextRetriever", "popSources", "RagSource"}
        ),
        new Question(
            "How does EnhancedContextProvider find similar code patterns for completion?",
            Difficulty.CROSS_MODULE,
            new String[]{"EnhancedContextProvider", "LuceneEmbeddingStore", "getSimilarCodePatterns"}
        ),
        new Question(
            "How does FontUtils apply the user-configured font size multiplier?",
            Difficulty.CROSS_MODULE,
            new String[]{"FontUtils", "OllamAssistUISettings", "getFontSizeMultiplier"}
        )
    );

    private QuestionCorpus() {}
}
