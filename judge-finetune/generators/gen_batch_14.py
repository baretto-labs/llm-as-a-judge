#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_14.jsonl (20 examples) — clôture du corpus à 200.

Composition imposée par les compteurs à 180 : 10 RAG_CONTEXT_RELEVANCE, 10 RAG_FAITHFULNESS,
9 parfait, 7 defaillant, 4 limite, 1 verbeux FAIL, 1 verbeux PASS.

Contextes réels extraits le 2026-09-14 (verification/contexts/), recopiés tels quels ;
[...] marque une troncature effectivement observée.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_batch_01 import example  # noqa: E402

EXAMPLES = []
add = EXAMPLES.append

SORTIE_RELEVANCE = ("(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de "
                    "recherche a retournés pour cette requête)")

# ── Contextes réels ───────────────────────────────────────────────────────────

CTX_NEO4J_COMPLETION = '''\
=== fr.baretto.ollamassist.completion.EnhancedCompletionService [Class] ===
Visibility: public
Fields:
  - private enterHandlerInstalled
  - private DEBOUNCE_DELAY_MS
  - private cache
  - private debouncer
  - private suggestionManager
  - private contextProvider
  - private DEBOUNCE_KEY_PREFIX

=== fr.baretto.ollamassist.git.MessageCleaner.clean(String) [Function] ===
Returns: java.lang.String
Parameters:
  - message: String

=== fr.baretto.ollamassist.completion.SuggestionEnterAction [Class] ===
Visibility: public
Annotations:
  - Slf4j
Fields:
  - private offset
  - private originalHandler
  - private suggestionManager

=== fr.baretto.ollamassist.completion.EnhancedCompletionService.requestCompletion(Editor) [Function] ===
Visibility: public
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.completion.InlineCompletionAction.actionPerformed(AnActionEvent) -[CALLS]-> fr.baretto.ollamassist.completion.Enh [...]

=== fr.baretto.ollamassist.completion.SuggestionManager [Class] ===
Visibility: public
Annotations:
  - Slf4j
Fields:
  - private loadingInlay
  - private currentInlay
  - private ERROR_MESSAGE_FORMAT
  - private currentSuggestion
  - private loadingRenderer'''

CTX_NEO4J_REFACTOR = '''\
=== fr.baretto.ollamassist.actions.refactor.RefactorAction.dismiss(Editor) [Function] ===
Visibility: private
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.actions.refactor.RefactorAction.createMouseAdapter(Project,Editor,String,TextRange,RefactoringInlayRenderer) -[CALLS]-> fr.bare [...]

=== fr.baretto.ollamassist.actions.refactor.RefactorAction [Class] ===
Visibility: public
Annotations:
  - Slf4j
Inheritance paths:
  fr.baretto.ollamassist.actions.refactor.RefactorAction -[EXTENDS]-> AnAction
Fields:
  - private MOUSE_LISTENER_KEY
  - private MOUSE_MOTION_LISTENER_KEY
  - private HIGHLIGHTER_KEY
  - [...]

=== fr.baretto.ollamassist.chat.service.Assistant.refactor(String,String,String) [Function] ===
Returns: TokenStream
Annotations:
  - UserMessage
Parameters:
  - language: String
  - code: String
  - refactorPrompt: String

=== fr.baretto.ollamassist.actions.refactor.RefactoringInlayRenderer [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.actions.refactor.RefactoringInlayRenderer -[IMPLEMENTS]-> EditorCustomElementRenderer
Fields:
  - private mousePosition
  - private backgroundColor
  - public declineBounds
  - [...]

=== fr.baretto.ollamassist.chat.rag.IndexRegistry.removeFromCurrentIndexation(String) [Function] ===
Visibility: public
Returns: void
Parameters:
  - projectId: String
Graph paths:
  fr.baretto.ollamassist.chat.rag.InitEmbeddingStoreTask.run(ProgressIndicator) -[CALLS]-> fr.baretto.ollamassist.chat.rag.IndexRegistry.re [...]'''

CTX_NEO4J_PARSERS = '''\
=== java.util.List<fr.baretto.ollamassist.chat.tools.ToolCallParser> [Class] ===

=== fr.baretto.ollamassist.chat.ui.ToolCallIndicator [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.ui.ToolCallIndicator -[EXTENDS]-> javax.swing.JPanel
Fields:
  - private detailsPanel
  - private PARAM_QUERY
  - private expanded
  - private MAPPER
  - private LABELS
  - private PRIMAR [...]

=== fr.baretto.ollamassist.chat.tools.ToolCallDetector [Class] ===
Visibility: public
Fields:
  - private parsers

=== fr.baretto.ollamassist.agent.tools.ToolApprovalHelper [Class] ===
Visibility: public
Annotations:
  - Slf4j
Fields:
  - private DEFAULT_TIMEOUT_MINUTES
  - private project

=== fr.baretto.ollamassist.chat.ui.MessagesPanel.addToolCallIndicator(String,String) [Function] ===
Visibility: public
Returns: void
Parameters:
  - toolName: String
  - argsJson: String
Graph paths:
  fr.baretto.ollamassist.chat.ui.OllamaContent.subscribe(MessageBusConnection) -[CALLS]-> fr.baretto.ollamassist.chat.ui [...]'''

CTX_NEO4J_APPROVAL = '''\
=== java.util.function.Consumer<fr.baretto.ollamassist.events.FileApprovalNotifier.ApprovalDecision> [Class] ===

=== fr.baretto.ollamassist.conversation.ConversationMessage.user(String) [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.conversation.ConversationMessage
Parameters:
  - content: String
Graph paths:
  fr.baretto.ollamassist.chat.ui.OllamaContent.subscribe(MessageBusConnection) -[CALLS]-> fr.baretto.ol [...]

=== fr.baretto.ollamassist.setting.panels.ActionsConfigPanel.getAutoApproveFileCreationCheckbox() [Function] ===
Visibility: public
Returns: javax.swing.JCheckBox
Graph paths:
  fr.baretto.ollamassist.setting.ConfigurationPanel.initializeListeners() -[CALLS]-> fr.baretto.ollamassist.setting.panels.ActionsConfigPanel.ge [...]

=== fr.baretto.ollamassist.agent.tools.ApprovalTimeoutException [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.agent.tools.ApprovalTimeoutException -[EXTENDS]-> java.lang.RuntimeException

=== fr.baretto.ollamassist.agent.tools.ToolApprovalHelper.requestApproval(String,String,String) [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.events.FileApprovalNotifier.ApprovalDecision
Parameters:
  - filePath: String
  - content: String
  - title: String
Graph paths:
  fr.baretto.ollamassist.agen [...]'''

CTX_LUCENE_BATCH = '''\
Method: fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline#processBatch
Signature: private void processBatch()
Body: {
    if (!isRunning || processingQueue.isEmpty())
        return;
    processingPhaser.arriveAndAwaitAdvance();
    processingLock.lock();
    try {
        List<String> currentBatch = new ArrayList<>(BATCH_SIZE);
        processingQueue.drainTo(currentBatch, BATCH_SIZE);
        if (!currentBatch.isEmpty [...]

Type: class fr.baretto.ollamassist.chat.rag.InitEmbeddingStoreTask extends Backgroundable
Field: private static final String FILES_PROGRESS_FORMAT = "%d/%d files";
Field: private static final String ERROR_PREFIX = "Failed - ";
Field: private final AtomicInteger processedFiles = new AtomicInteger(0);
Field: private final IndexRegistry indexationRegistry;
Field: private final DocumentIndexingPipeline documentIndexingPipeline; [...]

Type: class fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline implements AutoCloseable [...]

Method: fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline#flush [...]

Method: fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline#processSingleDocument [...]

Method: fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline#start [...]'''

CTX_LUCENE_COMBINE = '''\
Type: class fr.baretto.ollamassist.chat.rag.ContextRetriever implements ContentRetriever
Doc: * ContextRetriever is a custom {@link ContentRetriever} for OllamAssist.
 *
 * <p>
 * Its purpose is to fetch relevant context for a given {@link Query} from multiple sources:
 * <ul>
 *     <li>The main {@link ContentRetriever}, typically backed by an embedding store or an internal RAG engine.</li>
 *     <li>The user's workspace ({@ [...]

Type: class fr.baretto.ollamassist.chat.rag.tools.WebSearchTool
Field: private final DuckDuckGoContentRetriever duckDuckGo = new DuckDuckGoContentRetriever(2);
Method: public String searchOnDuckDuckGo(String query)

Method: fr.baretto.ollamassist.setting.OllamAssistUISettings#getContextPanelCollapsed [...]

DuckDuckGoContentRetriever.java [...]

Type: class fr.baretto.ollamassist.chat.rag.WorkspaceContextRetriever [...]

Type: class fr.baretto.ollamassist.chat.rag.HybridRetriever implements ContentRetriever [...]'''

# ══ RAG_CONTEXT_RELEVANCE (10) ═══════════════════════════════════════════════

add(example(
    meta={"id": "b14-001", "famille": "rag-completion-nettoyage-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_NEO4J_COMPLETION,
    requete="How does EnhancedCompletionService clean up raw LLM suggestions?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête porte sur le **nettoyage** des suggestions brutes par `EnhancedCompletionService`. Le contexte fournit le nœud de classe, avec les champs `cache`, `debouncer`, `suggestionManager`, `contextProvider` et `DEBOUNCE_DELAY_MS`, la fonction `requestCompletion(Editor)`, puis `MessageCleaner.clean(String)`, `SuggestionEnterAction` et `SuggestionManager`.
2. Vérification point par point : la classe visée est présente avec une de ses fonctions, la pertinence est donc acquise. La suffisance ne l'est pas : `requestCompletion` concerne le déclenchement d'une demande, pas le traitement de la réponse, et aucune fonction de nettoyage de cette classe ne figure au contexte. Un extrait tend un piège, `MessageCleaner.clean(String)` : le nom évoque exactement le nettoyage recherché, mais la classe appartient au paquet `git` et n'a aucun lien établi avec le service de complétion. S'en servir produirait une réponse fausse avec une apparence d'ancrage. Le bruit reste maîtrisé, les extraits restant dans le domaine de la complétion, à cette exception près.
3. Synthèse : la classe est là, la fonction de nettoyage non, et le seul extrait au nom prometteur appartient à un autre paquet. FAIL.
''',
    reason="Aucune fonction de nettoyage de la classe visée n'est fournie ; MessageCleaner.clean appartient au paquet git, sans lien établi.",
))

add(example(
    meta={"id": "b14-002", "famille": "rag-refactor-dismiss-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_NEO4J_REFACTOR,
    requete="What does the dismiss method do in RefactorAction?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : le premier extrait est le nœud de fonction `RefactorAction.dismiss(Editor)`, privé, sans valeur de retour, appelé depuis `createMouseAdapter(Project, Editor, String, TextRange, RefactoringInlayRenderer)`. Le deuxième est le nœud de classe `RefactorAction`, qui étend `AnAction` et déclare les clés `MOUSE_LISTENER_KEY`, `MOUSE_MOTION_LISTENER_KEY` et `HIGHLIGHTER_KEY`. Le quatrième est `RefactoringInlayRenderer`, qui implémente `EditorCustomElementRenderer`.
2. Vérification point par point : la méthode exactement demandée ouvre le contexte, donc la pertinence est immédiate. Sur la suffisance, l'ensemble permet de décrire ce que fait la méthode : elle est appelée depuis l'adaptateur de souris, elle opère sur un `Editor`, et les trois clés déclarées par la classe nomment ce qui est attaché à l'éditeur — deux écouteurs de souris et un surligneur — tandis que le renderer d'inlay figure parmi les collaborateurs. Le rapprochement est direct et ne demande pas d'invention. Deux extraits sont hors sujet, `Assistant.refactor` et `IndexRegistry.removeFromCurrentIndexation`, mais ils arrivent après l'information utile et ne prêtent pas à confusion.
3. Synthèse : la méthode visée, sa classe, ses clés et son appelant sont tous présents. PASS.
''',
    reason="Le nœud dismiss(Editor) et les clés d'écouteurs et de surligneur de la classe permettent de décrire ce que la méthode démonte.",
))

add(example(
    meta={"id": "b14-003", "famille": "rag-implementations-parser-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_NEO4J_PARSERS,
    requete="Which classes implement the ToolCallParser interface?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": False},
    thinking='''
1. Énumération des éléments clés : la requête demande la liste des implémentations de `ToolCallParser`. Le contexte fournit le type générique `List<ToolCallParser>`, `ToolCallIndicator` qui étend `JPanel`, `ToolCallDetector` avec son champ `parsers`, `ToolApprovalHelper` et `MessagesPanel.addToolCallIndicator`.
2. Vérification point par point : le nom de l'interface apparaît, dans un type générique et à travers le champ `parsers` de `ToolCallDetector`, ce qui suffit à une pertinence minimale. Mais **aucune arête `IMPLEMENTS` vers `ToolCallParser` n'est présente**, et aucune classe d'implémentation n'est nommée : le contexte ne permet pas de répondre. C'est d'autant plus net que la question porte sur une relation d'héritage, précisément ce qu'un graphe sait exprimer — son absence ici est donc concluante, pas ambiguë. Quant au bruit, trois extraits sur cinq relèvent de l'interface graphique ou de l'approbation d'outils et n'ont de commun que le préfixe `Tool`, ce qui égare sans rien apporter.
3. Synthèse : l'interface est nommée mais aucune implémentation ne l'est, et la majorité des extraits ne tient qu'à une parenté de nom. FAIL.
''',
    reason="Aucune arête IMPLEMENTS vers ToolCallParser ni aucune classe d'implémentation nommée ; les extraits ne partagent que le préfixe Tool.",
))

add(example(
    meta={"id": "b14-004", "famille": "rag-approbation-fichier-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "limite", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_NEO4J_APPROVAL,
    requete="How does FileCreator request user approval via FileApprovalNotifier?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête porte sur le couple `FileCreator` et `FileApprovalNotifier`. Le contexte fournit `Consumer<FileApprovalNotifier.ApprovalDecision>`, la fonction `ToolApprovalHelper.requestApproval(String, String, String)` renvoyant une `ApprovalDecision`, `ApprovalTimeoutException`, la case à cocher `getAutoApproveFileCreationCheckbox()` et `ConversationMessage.user(String)`.
2. Vérification point par point : le mécanisme d'approbation est largement couvert — le type de décision, la fonction qui la demande avec ses trois paramètres dont le chemin et le contenu, l'exception de délai dépassé, et jusqu'au réglage d'approbation automatique. La pertinence est donc forte. Mais `FileCreator` **n'apparaît dans aucun extrait**, et la fonction `requestApproval` fournie appartient à `ToolApprovalHelper`, une autre classe. Le contexte montre donc comment une approbation est demandée dans le projet, sans établir que `FileCreator` passe par ce chemin ni comment. La requête portant explicitement sur cette classe, la suffisance n'est pas atteinte. Le bruit reste faible et thématiquement cohérent.
3. Synthèse : le contexte est riche et directement sur le sujet de l'approbation, mais la classe interrogée en est absente, et l'attribuer serait une inférence. FAIL.
''',
    reason="Le mécanisme d'approbation est bien couvert, mais FileCreator est absent : requestApproval y appartient à ToolApprovalHelper.",
))

add(example(
    meta={"id": "b14-005", "famille": "rag-constantes-lot-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_LUCENE_BATCH,
    requete="How does DocumentIndexingPipeline process documents in batches?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : le premier extrait est le corps de `DocumentIndexingPipeline#processBatch`, qui montre la garde sur `isRunning` et la file vide, la synchronisation par `processingPhaser.arriveAndAwaitAdvance()`, la prise du verrou `processingLock`, puis le drainage `processingQueue.drainTo(currentBatch, BATCH_SIZE)`. Suivent la classe elle-même, déclarée `implements AutoCloseable`, et ses méthodes `flush`, `processSingleDocument` et `start`.
2. Vérification point par point : la méthode de traitement par lots est fournie **avec son corps**, ce qui est décisif — la requête porte sur le mécanisme, et le mécanisme est visible : garde d'entrée, barrière de synchronisation, verrou, puis extraction d'au plus `BATCH_SIZE` éléments de la file vers une liste. Les méthodes voisines situent le cycle de vie complet. Le contexte est donc pertinent et suffisant pour décrire le traitement par lots. Le bruit est limité à deux extraits, dont `InitEmbeddingStoreTask` qui reste dans le même domaine d'indexation.
3. Synthèse : le corps de la méthode centrale est présent, entouré du cycle de vie de la classe. PASS.
''',
    reason="Le corps de processBatch montre garde, phaser, verrou et drainTo vers un lot ; les méthodes voisines complètent le cycle de vie.",
))

add(example(
    meta={"id": "b14-006", "famille": "rag-combinaison-sources-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_LUCENE_COMBINE,
    requete="Which sources does ContextRetriever fetch context from?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : le premier extrait est la classe `ContextRetriever`, qui implémente `ContentRetriever`, avec une documentation énonçant que son objet est de récupérer du contexte « from multiple sources » et amorçant une liste — le `ContentRetriever` principal adossé à un magasin d'embeddings ou à un moteur RAG interne, puis l'espace de travail de l'utilisateur. Suivent `WebSearchTool`, qui déclare un champ `DuckDuckGoContentRetriever`, puis les classes `WorkspaceContextRetriever` et `HybridRetriever`.
2. Vérification point par point : la classe visée ouvre le contexte et sa documentation répond directement à la question posée, qui porte sur les sources. La liste documentaire est tronquée, mais les deux premières sources y sont lisibles et les extraits suivants nomment les classes correspondantes, `WorkspaceContextRetriever` pour l'espace de travail et `DuckDuckGoContentRetriever` pour la recherche web. Le recoupement entre la documentation et les nœuds de classes rend la réponse complète sans inférence hasardeuse. Le bruit se limite à un réglage d'interface et à quelques extraits périphériques du même domaine.
3. Synthèse : la documentation de la classe visée énumère les sources, et les classes correspondantes figurent au contexte. PASS.
''',
    reason="La documentation de ContextRetriever énumère les sources, recoupée par les nœuds WorkspaceContextRetriever et DuckDuckGoContentRetriever.",
))

add(example(
    meta={"id": "b14-007", "famille": "rag-valeur-constante-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_LUCENE_BATCH,
    requete="What are the values of BATCH_SIZE and SYNCHRONOUS_BATCH_SIZE in DocumentIndexingPipeline?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête demande les **valeurs** de deux constantes. Le contexte fournit le corps de `processBatch`, où `BATCH_SIZE` apparaît deux fois — dans `new ArrayList<>(BATCH_SIZE)` et dans `processingQueue.drainTo(currentBatch, BATCH_SIZE)` — ainsi que la classe et plusieurs de ses méthodes, plus les champs d'`InitEmbeddingStoreTask`.
2. Vérification point par point : la classe et la constante sont bien présentes, donc le contexte est pertinent. Mais aucune déclaration de `BATCH_SIZE` ne figure au contexte : la constante n'y est qu'**utilisée**, jamais définie, et sa valeur reste donc inconnue. `SYNCHRONOUS_BATCH_SIZE` n'apparaît pas du tout. L'écart est instructif : les champs d'`InitEmbeddingStoreTask`, eux, sont fournis avec leurs valeurs — `FILES_PROGRESS_FORMAT`, `ERROR_PREFIX` — ce qui montre que l'extraction sait les rendre quand elles sont dans le fragment retenu. Ici elles ne le sont pas. Répondre exigerait de deviner un nombre. Le bruit reste maîtrisé.
3. Synthèse : la constante est utilisée dans le corps fourni mais jamais déclarée, et la seconde est absente : les valeurs demandées ne sont pas dans le contexte. FAIL.
''',
    reason="BATCH_SIZE n'est qu'utilisée, jamais déclarée dans les extraits, et SYNCHRONOUS_BATCH_SIZE en est absente : aucune valeur n'est lisible.",
))

add(example(
    meta={"id": "b14-008", "famille": "rag-combinaison-sources-lucene-verbeux", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_LUCENE_COMBINE,
    requete="Is DuckDuckGo search integrated into the context retrieval, and through which class?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête demande si la recherche DuckDuckGo est intégrée et par quelle classe. Le contexte contient `WebSearchTool`, qui déclare `private final DuckDuckGoContentRetriever duckDuckGo = new DuckDuckGoContentRetriever(2);` et la méthode `searchOnDuckDuckGo(String query)`, un extrait nommant le fichier `DuckDuckGoContentRetriever.java`, et la documentation de `ContextRetriever` sur ses sources multiples.
2. Vérification point par point : la réponse est directement lisible. `WebSearchTool` porte une instance de `DuckDuckGoContentRetriever`, construite avec l'argument `2`, et expose une méthode de recherche : la classe d'intégration est nommée, et la déclaration de champ est donnée avec son initialisation complète. Le contexte est donc pertinent et suffisant. Il est verbeux — dix extraits, dont un réglage d'affichage et plusieurs classes de récupération seulement effleurées — mais cette abondance ne noie pas l'information : le champ décisif figure dans le deuxième extrait, et les extraits périphériques relèvent tous du même domaine de récupération de contexte. La verbosité d'un contexte ne se juge pas à son volume mais à sa capacité à enfouir la réponse, ce qui n'est pas le cas ici.
3. Synthèse : la classe d'intégration et la déclaration du champ sont explicites, et le volume n'enfouit pas la réponse. PASS.
''',
    reason="WebSearchTool déclare le champ DuckDuckGoContentRetriever avec son initialisation, et le volume du contexte n'enfouit pas la réponse.",
))

add(example(
    meta={"id": "b14-009", "famille": "rag-refactor-classe-parente-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_NEO4J_REFACTOR,
    requete="What class does RefactorAction extend, and what does RefactoringInlayRenderer implement?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête porte sur deux relations d'héritage. Le contexte fournit le nœud `RefactorAction` avec l'arête `-[EXTENDS]-> AnAction`, et le nœud `RefactoringInlayRenderer` avec l'arête `-[IMPLEMENTS]-> EditorCustomElementRenderer`.
2. Vérification point par point : les deux relations demandées sont présentes explicitement, chacune sous forme d'arête nommée, ce qui est exactement la forme d'information qu'un index de graphe est censé fournir pour ce type de question. Le contexte est donc pertinent et suffisant, sans aucune inférence à faire. Les trois autres extraits — `dismiss`, `Assistant.refactor`, `IndexRegistry.removeFromCurrentIndexation` — sont sans rapport avec la question posée, mais le premier concerne la classe visée et les deux autres sont brefs : rien qui masque les deux arêtes utiles.
3. Synthèse : les deux relations d'héritage demandées figurent explicitement au contexte. PASS.
''',
    reason="Les deux arêtes demandées sont explicites : EXTENDS AnAction et IMPLEMENTS EditorCustomElementRenderer.",
))

add(example(
    meta={"id": "b14-010", "famille": "rag-detecteur-outils-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "limite", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE", contexte=CTX_NEO4J_PARSERS,
    requete="Does ToolCallDetector hold several parsers?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": False},
    thinking='''
1. Énumération des éléments clés : la requête est étroite — `ToolCallDetector` détient-il plusieurs parseurs ? Le contexte fournit le nœud de classe `ToolCallDetector`, dont l'unique champ listé est `parsers`, ainsi que le type `java.util.List<fr.baretto.ollamassist.chat.tools.ToolCallParser>`.
2. Vérification point par point : la classe visée est présente, donc le contexte est pertinent. Sur la suffisance, la question appelle une réponse simple, et les deux extraits la portent : le champ au pluriel et la présence, dans le même contexte, du type liste paramétré par `ToolCallParser` établissent que le détecteur en détient une collection. C'est assez pour répondre à cette question précise, là où la question plus large des implémentations resterait, elle, sans réponse. En revanche le bruit n'est pas maîtrisé : trois extraits sur cinq — un panneau Swing, une aide à l'approbation, une méthode d'affichage — n'ont de rapport que le préfixe `Tool`, et l'information utile tient dans deux lignes noyées au milieu.
3. Synthèse : le contexte répond à la question posée, mais la majorité de son volume est hors sujet. FAIL.
''',
    reason="Le champ parsers et le type List<ToolCallParser> répondent à la question, mais trois extraits sur cinq ne tiennent qu'au préfixe Tool.",
))

# ══ RAG_FAITHFULNESS (10) ════════════════════════════════════════════════════

add(example(
    meta={"id": "b14-011", "famille": "rag-fidelite-nettoyage-invente", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": True, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_NEO4J_COMPLETION,
    requete="How does EnhancedCompletionService clean up raw LLM suggestions?",
    reponse='''
## Le pipeline de nettoyage

`EnhancedCompletionService` confie le nettoyage à sa méthode privée `processSuggestion(String rawSuggestion, Editor editor)`, appelée dès la réception de la réponse du modèle.

Celle-ci enchaîne deux traitements :

1. **Retrait des balises de bloc de code** — la méthode `removeCodeBlockMarkers(String suggestion)` supprime les triples accents graves que le modèle ajoute presque systématiquement autour du code.
2. **Suppression de la répétition de début de ligne** — si la suggestion recommence par le texte déjà présent à gauche du curseur, ce préfixe est retiré pour éviter la duplication à l'insertion.

## Pourquoi c'est nécessaire

Un modèle de complétion répond comme s'il rédigeait un extrait autonome. Sans ce nettoyage, l'insertion produirait des marqueurs Markdown au milieu du fichier et dupliquerait le début de la ligne courante.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit le nœud de classe `EnhancedCompletionService` avec ses champs, la fonction `requestCompletion(Editor)`, puis `MessageCleaner.clean(String)`, `SuggestionEnterAction` et `SuggestionManager`. Aucun corps de méthode.
2. Vérification point par point : ni `processSuggestion` ni `removeCodeBlockMarkers` n'apparaissent dans les extraits. La seule fonction de la classe visée qui y figure est `requestCompletion`, qui n'est pas citée par la réponse. Les deux traitements décrits — retrait des triples accents graves, suppression du préfixe répété — ne sont soutenus par aucun extrait, pas plus que la signature avancée pour la méthode principale. Ces affirmations décrivent pourtant fidèlement le code réel : c'est précisément ce qui rend le cas instructif, puisqu'une réponse exacte doit ici être rejetée faute d'ancrage. Le contexte contenait par ailleurs un piège que la réponse n'a pas relevé — `MessageCleaner.clean(String)`, dont le nom évoque le nettoyage mais qui appartient au paquet `git` — et l'ignorer ne rachète pas le fait d'avoir puisé ailleurs que dans les extraits. Rien de ce qui est effectivement repris du contexte n'est déformé, la réponse n'en reprenant rien.
3. Synthèse : la sortie décrit deux méthodes et un enchaînement absents du contexte, dont aucun corps n'était fourni. FAIL.
''',
    reason="processSuggestion et removeCodeBlockMarkers sont absents du contexte, qui ne contient que des nœuds sans corps de méthode.",
))

add(example(
    meta={"id": "b14-012", "famille": "rag-fidelite-completion-etayee", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_NEO4J_COMPLETION,
    requete="How does EnhancedCompletionService clean up raw LLM suggestions?",
    reponse='''
Le contexte ne permet pas de répondre à la question posée : aucune méthode de nettoyage de `EnhancedCompletionService` n'y figure.

Ce qu'il établit : la classe déclare les champs `cache`, `debouncer`, `suggestionManager`, `contextProvider`, `enterHandlerInstalled`, ainsi que `DEBOUNCE_DELAY_MS` et `DEBOUNCE_KEY_PREFIX`, ce qui indique une mise en cache et un anti-rebond. Sa seule fonction fournie est `requestCompletion(Editor)`, appelée depuis `InlineCompletionAction.actionPerformed(AnActionEvent)` — c'est le déclenchement de la demande, pas le traitement de la réponse.

Une mise en garde : le contexte contient `MessageCleaner.clean(String)`, dont le nom évoque le nettoyage recherché, mais cette classe appartient au paquet `git` et aucun lien avec le service de complétion n'apparaît dans les extraits. Je ne l'utilise donc pas pour répondre.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte donne les champs du nœud de classe, la fonction `requestCompletion(Editor)` avec son chemin d'appel depuis `InlineCompletionAction.actionPerformed(AnActionEvent)`, et trois nœuds voisins dont `MessageCleaner.clean(String)`.
2. Vérification point par point : la liste de champs citée correspond exactement à celle du contexte, et la lecture qui en est faite — mise en cache et anti-rebond — est prudemment introduite comme une indication tirée des noms, pas comme un fait. Le chemin d'appel est repris fidèlement, et la distinction entre déclencher une demande et traiter une réponse est juste au regard de ce que montre le contexte. Aucune méthode absente n'est invoquée. Le point remarquable est la mise en garde finale : la sortie identifie le piège du nom trompeur, en indique la raison — un autre paquet, aucun lien établi — et refuse explicitement de s'en servir. C'est exactement la discipline attendue en monde fermé.
3. Synthèse : tout est étayé, rien n'est inventé, et l'extrait au nom trompeur est écarté avec justification. PASS.
''',
    reason="S'en tient aux champs et à la fonction réellement fournis, et écarte explicitement MessageCleaner.clean comme homonyme d'un autre paquet.",
))

add(example(
    meta={"id": "b14-013", "famille": "rag-fidelite-dismiss-etayee", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_NEO4J_REFACTOR,
    requete="What does the dismiss method do in RefactorAction?",
    reponse='''
D'après le contexte :

- `RefactorAction.dismiss(Editor)` est une méthode privée sans valeur de retour, qui prend l'éditeur en paramètre.
- Elle est appelée depuis `RefactorAction.createMouseAdapter(Project, Editor, String, TextRange, RefactoringInlayRenderer)`, donc depuis la mise en place de l'adaptateur de souris.
- La classe déclare les clés `MOUSE_LISTENER_KEY`, `MOUSE_MOTION_LISTENER_KEY` et `HIGHLIGHTER_KEY`, et collabore avec `RefactoringInlayRenderer`.

Le corps de la méthode n'est pas fourni. Ce que le contexte permet de dire, c'est qu'elle intervient sur un éditeur dans un dispositif comportant deux écouteurs de souris, un surligneur et un renderer d'inlay ; le détail de ce qu'elle retire ou restaure n'y figure pas.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte donne le nœud `dismiss(Editor)` avec sa visibilité, son type de retour et son paramètre, le chemin d'appel depuis `createMouseAdapter(...)` avec sa signature complète, le nœud de classe avec ses trois clés, et le nœud `RefactoringInlayRenderer`.
2. Vérification point par point : les trois affirmations correspondent chacune à un élément explicite, signature de l'appelant comprise. La lecture des clés est correctement bornée : la sortie dit que la méthode intervient dans un dispositif comportant ces éléments, sans affirmer qu'elle les retire un à un — ce que le contexte ne montre pas. Le dernier paragraphe pose explicitement la limite, l'absence de corps, et en tire la bonne conséquence. Aucune invention, aucune déformation.
3. Synthèse : affirmations étayées, inférence sur les clés bornée à ce que permet une liste de champs, et limite du contexte explicitement posée. PASS.
''',
    reason="Signature, appelant et clés sont repris fidèlement, et l'absence de corps est posée comme limite au lieu d'être comblée.",
))

add(example(
    meta={"id": "b14-014", "famille": "rag-fidelite-dismiss-detaillee", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_NEO4J_REFACTOR,
    requete="What does the dismiss method do in RefactorAction?",
    reponse='''
`dismiss(Editor)` démonte l'ensemble du dispositif de prévisualisation d'un refactoring : elle retire l'écouteur de souris et l'écouteur de mouvement enregistrés sous `MOUSE_LISTENER_KEY` et `MOUSE_MOTION_LISTENER_KEY`, supprime le surligneur de différences stocké sous `HIGHLIGHTER_KEY`, puis dispose l'inlay `RefactoringInlayRenderer` attaché à l'éditeur.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit le nœud `dismiss(Editor)` — visibilité, type de retour, paramètre, appelant — et le nœud de classe listant `MOUSE_LISTENER_KEY`, `MOUSE_MOTION_LISTENER_KEY` et `HIGHLIGHTER_KEY`, ainsi que le nœud `RefactoringInlayRenderer`. Aucun corps de méthode n'est fourni.
2. Vérification point par point : les noms cités existent bien dans le contexte, et les citations ne sont pas déformées — c'est le seul contrôle que la sortie satisfait. En revanche, l'**action** attribuée à la méthode n'est nulle part étayée : rien ne dit qu'elle retire ces écouteurs, supprime ce surligneur ou dispose cet inlay. La sortie construit un comportement plausible à partir d'une liste de noms de clés, ce qui est une inférence et non une lecture. La différence avec une formulation acceptable est mince mais décisive : dire que la méthode intervient dans un dispositif comportant ces éléments est étayé, affirmer qu'elle les retire dans cet ordre ne l'est pas. La description se trouve être exacte dans la codebase, ce qui ne la rend pas étayée pour autant. Le qualificatif « surligneur de différences » ajoute même une précision que le seul nom de clé ne porte pas.
3. Synthèse : les noms viennent du contexte, mais le comportement décrit est déduit de noms de clés, sans aucun corps de méthode pour l'établir. FAIL.
''',
    reason="Le comportement attribué à dismiss est déduit de noms de clés : aucun corps de méthode ne figure au contexte pour l'étayer.",
))

add(example(
    meta={"id": "b14-015", "famille": "rag-fidelite-approbation-mauvaise-classe", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_NEO4J_APPROVAL,
    requete="How does FileCreator request user approval via FileApprovalNotifier?",
    reponse='''
`FileCreator` appelle sa méthode `requestApproval(String filePath, String content, String title)`, qui publie une demande sur le sujet du bus de messages et attend une `ApprovalDecision`. Si l'utilisateur ne répond pas dans le délai imparti, une `ApprovalTimeoutException` est levée.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit `ToolApprovalHelper.requestApproval(String, String, String)` renvoyant une `FileApprovalNotifier.ApprovalDecision`, le type `Consumer<ApprovalDecision>`, `ApprovalTimeoutException -[EXTENDS]-> RuntimeException`, et un réglage d'approbation automatique. `FileCreator` n'y figure pas.
2. Vérification point par point : la signature citée est exacte, mais la classe à laquelle elle est attribuée ne l'est pas. Le contexte rattache sans ambiguïté `requestApproval` à `ToolApprovalHelper` ; écrire que `FileCreator` appelle **sa** méthode déplace la fonction d'une classe à une autre, et rien dans les extraits n'établit même que `FileCreator` participe à ce mécanisme. La mention du sujet de bus de messages n'est pas davantage étayée : le contexte montre un type de décision et un consommateur, jamais une publication sur un topic. Le lien entre l'exception de délai et cette méthode est également supposé — l'exception existe bien au contexte, son déclenchement par `requestApproval` n'y est pas montré. Les éléments repris ne sont pas déformés pris isolément, d'où le seul contrôle satisfait.
3. Synthèse : la méthode est attribuée à une classe absente du contexte, alors que les extraits la rattachent explicitement à une autre. FAIL.
''',
    reason="Le contexte rattache requestApproval à ToolApprovalHelper ; FileCreator n'y figure pas, et la publication sur un topic n'est pas montrée.",
))

add(example(
    meta={"id": "b14-016", "famille": "rag-fidelite-approbation-etayee", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_NEO4J_APPROVAL,
    requete="How does FileCreator request user approval via FileApprovalNotifier?",
    reponse='''
`FileCreator` n'apparaît pas dans le contexte fourni : je ne peux donc pas décrire comment cette classe demande l'approbation.

Ce que le contexte établit sur le mécanisme d'approbation lui-même :

- `ToolApprovalHelper.requestApproval(String filePath, String content, String title)` renvoie une `FileApprovalNotifier.ApprovalDecision` — c'est la fonction de demande visible, portée par `ToolApprovalHelper`.
- Le type `Consumer<FileApprovalNotifier.ApprovalDecision>` apparaît, ce qui indique une remise de décision par rappel.
- `ApprovalTimeoutException` existe et étend `RuntimeException`.
- Un réglage d'interface expose une case `getAutoApproveFileCreationCheckbox()`, donc l'approbation peut être court-circuitée par configuration.

Rien n'établit en revanche que `FileCreator` passe par ce chemin, ni comment la demande est publiée ou attendue.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte contient la fonction `requestApproval` de `ToolApprovalHelper` avec sa signature et son type de retour, le type `Consumer<ApprovalDecision>`, l'exception de délai avec son héritage, et la case à cocher d'approbation automatique.
2. Vérification point par point : les quatre affirmations correspondent exactement aux extraits, y compris le rattachement de `requestApproval` à `ToolApprovalHelper`, que la sortie prend soin de préciser au lieu de l'attribuer à la classe interrogée. Les lectures tirées des noms — remise par rappel, court-circuit par configuration — sont introduites comme des indications, ce que la forme des extraits autorise. Le constat d'ouverture et la réserve finale délimitent correctement ce que le contexte ne couvre pas, sans combler par déduction. Aucune invention, aucune déformation.
3. Synthèse : chaque élément est tiré du contexte, la classe absente est signalée comme telle, et l'attribution de la fonction est faite à la bonne classe. PASS.
''',
    reason="Rattache requestApproval à ToolApprovalHelper comme le fait le contexte, et constate l'absence de FileCreator au lieu de la combler.",
))

add(example(
    meta={"id": "b14-017", "famille": "rag-fidelite-constante-chiffree", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_LUCENE_BATCH,
    requete="How does DocumentIndexingPipeline process documents in batches?",
    reponse='''
`processBatch()` draine la file d'attente par paquets de **10 documents** — la constante `BATCH_SIZE` vaut 10 — après avoir vérifié que le pipeline tourne et que la file n'est pas vide. En traitement synchrone, la taille passe à 100 via `SYNCHRONOUS_BATCH_SIZE`.

La méthode prend le verrou `processingLock` et synchronise les producteurs avec `processingPhaser.arriveAndAwaitAdvance()` avant de drainer.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit le corps de `processBatch`, qui montre la garde `if (!isRunning || processingQueue.isEmpty()) return;`, l'appel `processingPhaser.arriveAndAwaitAdvance()`, la prise de `processingLock`, puis `new ArrayList<>(BATCH_SIZE)` et `processingQueue.drainTo(currentBatch, BATCH_SIZE)`.
2. Vérification point par point : le second paragraphe est entièrement étayé — verrou, phaser et garde figurent littéralement dans le corps fourni, et les citations sont exactes. Le premier ne l'est pas. La valeur 10 attribuée à `BATCH_SIZE` n'apparaît nulle part : la constante est utilisée deux fois dans le corps, jamais déclarée. `SYNCHRONOUS_BATCH_SIZE` et sa valeur de 100 sont absentes du contexte dans son intégralité. Les deux chiffres correspondent au code réel, et c'est le piège : ils donnent à la réponse une précision qui semble venir d'une lecture attentive, alors qu'ils viennent d'ailleurs. Le contexte permettait pourtant une formulation juste — drainer au plus `BATCH_SIZE` éléments, valeur non visible.
3. Synthèse : le mécanisme décrit est correct et étayé, mais les deux valeurs chiffrées avancées sont absentes du contexte. FAIL.
''',
    reason="Les valeurs 10 et 100 n'apparaissent pas : BATCH_SIZE n'est qu'utilisée dans le corps fourni, et SYNCHRONOUS_BATCH_SIZE en est absente.",
))

add(example(
    meta={"id": "b14-018", "famille": "rag-fidelite-lot-borne", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "limite", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_LUCENE_BATCH,
    requete="How does DocumentIndexingPipeline process documents in batches?",
    reponse='''
D'après le corps fourni de `processBatch()` :

1. La méthode sort immédiatement si le pipeline ne tourne pas (`!isRunning`) ou si la file `processingQueue` est vide.
2. Elle franchit une barrière de synchronisation avec `processingPhaser.arriveAndAwaitAdvance()`.
3. Elle prend le verrou `processingLock`.
4. Elle alloue une liste dimensionnée à `BATCH_SIZE` et y draine au plus `BATCH_SIZE` éléments de la file, via `processingQueue.drainTo(currentBatch, BATCH_SIZE)`.

La valeur de `BATCH_SIZE` n'est pas visible : la constante est utilisée, jamais déclarée dans les extraits. Le corps est par ailleurs tronqué après le test `if (!currentBatch.isEmpty`, donc le traitement effectif du lot n'est pas observable.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit le corps de `processBatch` jusqu'à sa troncature, avec la garde d'entrée, le phaser, le verrou, l'allocation et le drainage.
2. Vérification point par point : les quatre étapes énumérées correspondent ligne à ligne au corps fourni, et les identifiants cités sont exacts, y compris la forme de l'appel `drainTo`. La formulation « au plus `BATCH_SIZE` éléments » est fidèle à la sémantique de `drainTo` sans rien ajouter. Les deux réserves finales sont justes et précises : la constante est effectivement utilisée sans être déclarée, et la troncature est signalée au point exact où elle survient, ce qui délimite correctement ce qui reste inobservable. Aucune valeur n'est avancée, aucune méthode absente n'est invoquée.
3. Synthèse : la réponse est incomplète, puisqu'elle ne peut décrire ni la valeur du lot ni le traitement effectif, mais chaque affirmation est étayée et chaque lacune est nommée avec sa cause. PASS.
''',
    reason="Chaque étape correspond au corps fourni, la valeur de BATCH_SIZE est déclarée non visible et la troncature est signalée à l'endroit exact.",
))

add(example(
    meta={"id": "b14-019", "famille": "rag-fidelite-sources-etayee", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_LUCENE_COMBINE,
    requete="Which sources does ContextRetriever fetch context from?",
    reponse='''
La documentation de `ContextRetriever` indique que la classe récupère du contexte depuis plusieurs sources, et la liste commence par :

- le `ContentRetriever` principal, adossé selon la documentation à un magasin d'embeddings ou à un moteur RAG interne ;
- l'espace de travail de l'utilisateur.

La liste est tronquée à cet endroit dans l'extrait. Deux autres classes du contexte se rattachent au sujet : `WorkspaceContextRetriever`, qui correspond à la source « espace de travail », et `WebSearchTool`, qui déclare un champ `DuckDuckGoContentRetriever` initialisé par `new DuckDuckGoContentRetriever(2)`.

Le contexte ne montre pas comment ces sources sont combinées, ni dans quel ordre.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit la classe `ContextRetriever` avec sa documentation évoquant plusieurs sources et amorçant une liste, la classe `WebSearchTool` avec sa déclaration de champ complète, ainsi que les nœuds `WorkspaceContextRetriever` et `HybridRetriever`.
2. Vérification point par point : les deux sources citées proviennent littéralement de la documentation, dont la formulation sur le magasin d'embeddings et le moteur RAG interne est reprise fidèlement. La troncature est signalée à l'endroit où elle se produit, ce qui évite de présenter une liste partielle comme exhaustive. Le rattachement de `WorkspaceContextRetriever` à la source « espace de travail » est une correspondance directe entre deux éléments du contexte, et la citation du champ de `WebSearchTool` est exacte, argument compris. La réserve finale est juste : aucun corps de méthode ne montre la combinaison des résultats.
3. Synthèse : affirmations tirées de la documentation et des nœuds fournis, troncature signalée, et absence du mécanisme de combinaison explicitement posée. PASS.
''',
    reason="Les sources citées viennent de la documentation, la troncature est signalée, et le champ DuckDuckGoContentRetriever est cité exactement.",
))

add(example(
    meta={"id": "b14-020", "famille": "rag-fidelite-hybride-borne", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "limite", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS", contexte=CTX_LUCENE_COMBINE,
    requete="What is the role of HybridRetriever relative to ContextRetriever?",
    reponse='''
Le contexte établit peu de choses sur ce point précis.

Ce qui est visible : `HybridRetriever` et `ContextRetriever` implémentent toutes deux `ContentRetriever`. La documentation de `ContextRetriever` indique par ailleurs que sa source principale est « the main ContentRetriever, typically backed by an embedding store or an internal RAG engine ».

Ce qui ne l'est pas : aucun extrait ne montre de relation directe entre les deux classes — ni composition, ni appel, ni héritage. L'hypothèse que `HybridRetriever` tienne le rôle de ce `ContentRetriever` principal est cohérente avec les deux éléments ci-dessus, mais elle n'est pas établie par le contexte, qui ne contient aucun corps de méthode ni aucun champ de `ContextRetriever`.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte donne `ContextRetriever implements ContentRetriever` avec sa documentation, et `HybridRetriever implements ContentRetriever`. Aucun extrait ne relie les deux classes.
2. Vérification point par point : les deux relations d'implémentation citées figurent explicitement, et la phrase de documentation est reprise littéralement, guillemets compris. Le point délicat est l'hypothèse formulée dans le dernier paragraphe : la sortie l'énonce, en indique la cohérence, puis dit explicitement qu'elle **n'est pas établie** par le contexte, en donnant la raison — aucun champ ni corps de `ContextRetriever` n'est fourni. Une hypothèse présentée comme telle, avec sa limite, ne constitue pas une invention ; l'aurait été une affirmation du même contenu au présent de l'indicatif. Aucune citation n'est déformée.
3. Synthèse : la réponse n'établit pas grand-chose, mais tout ce qu'elle avance est étayé, et l'hypothèse avancée est explicitement marquée comme non établie. PASS.
''',
    reason="Les deux relations d'implémentation sont exactes, la citation est littérale, et l'hypothèse sur le rôle est explicitement donnée pour non établie.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
