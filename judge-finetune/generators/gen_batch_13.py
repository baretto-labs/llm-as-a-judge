#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_13.jsonl (15 examples, tâches RAG).

Contextes réels extraits le 2026-09-14 (verification/contexts/). Recopiés tels quels ;
[...] marque une troncature effectivement observée à la lecture.

Ce lot exploite un cas remarquable : la question sur l'interface Assistant affiche 75 % de
couverture d'indices alors que l'interface est absente du contexte — la couverture ne mesure
qu'une présence de sous-chaîne, jamais la suffisance.
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

CTX_NEO4J_PIPELINE = '''\
=== fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline [Class] ===
Visibility: public
Fields:
  - private INDEXED_COUNT_FORMAT
  - private isRunning
  - private fileRetries
  - private processingLock
  - private PROCESSING_ERROR_FORMAT
  - private project
  - private scheduler
  - private LOG_INTERVAL
  - private processin [...]

=== Document [Class] ===

=== fr.baretto.ollamassist.chat.rag.CorruptedIndexException [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.CorruptedIndexException -[EXTENDS]-> java.lang.RuntimeException

=== fr.baretto.ollamassist.chat.rag.IndexRegistry.isIndexed(String) [Function] ===
Visibility: public
Returns: boolean
Parameters:
  - projectId: String
Graph paths:
  fr.baretto.ollamassist.chat.rag.ProjectFileListener.load() -[CALLS]-> fr.baretto.ollamassist.chat.rag.IndexRegistry.isIndexed(String) [...]

=== fr.baretto.ollamassist.chat.askfromcode.EditorListener.handleEditorRelease(Editor) [Function] ===
Visibility: private
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.chat.askfromcode.EditorListener.attachListeners() -[CALLS]-> fr.baretto.ollamassist.chat.askfromcode.EditorListener.handleEdi [...]'''

CTX_NEO4J_PARSER = '''\
=== fr.baretto.ollamassist.chat.tools.BracketCallParser [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.tools.BracketCallParser -[IMPLEMENTS]-> fr.baretto.ollamassist.chat.tools.ToolCallParser
Fields:
  - private BRACKET_PATTERN
  - private MAX_ARGUMENTS

=== fr.baretto.ollamassist.chat.tools.ToolCallParser.parse(String) [Function] ===
Returns: java.util.Optional<fr.baretto.ollamassist.chat.tools.DetectedToolCall>
Parameters:
  - text: String
Graph paths:
  fr.baretto.ollamassist.chat.tools.ToolCallDetector.detect(String) -[CALLS]-> fr.baretto.ollamassist.chat.tools.ToolCallParse [...]

=== fr.baretto.ollamassist.chat.tools.BracketCallParser.parse(String) [Function] ===
Visibility: public
Returns: java.util.Optional<fr.baretto.ollamassist.chat.tools.DetectedToolCall>
Annotations:
  - Override
Parameters:
  - text: String
Graph paths:
  fr.baretto.ollamassist.chat.tools.BracketCallParser.parse(String) -[CALLS]-> [...]

=== java.util.List<fr.baretto.ollamassist.chat.tools.ToolCallParser> [Class] ===

=== fr.baretto.ollamassist.component.LogCellRenderer [Class] ===
Visibility: private
Inheritance paths:
  fr.baretto.ollamassist.component.LogCellRenderer -[EXTENDS]-> javax.swing.DefaultListCellRenderer'''

CTX_NEO4J_ASSISTANT = '''\
=== fr.baretto.ollamassist.conversation.ConversationMessage.assistant(String) [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.conversation.ConversationMessage
Parameters:
  - content: String
Graph paths:
  fr.baretto.ollamassist.chat.ui.OllamaContent.subscribe(MessageBusConnection) -[CALLS]-> fr.baretto.ollamas [...]

=== fr.baretto.ollamassist.completion.LightModelService.handleSuggestion(Editor) [Function] ===
Visibility: public
Returns: void
Parameters:
  - editor: Editor
Graph paths:
  fr.baretto.ollamassist.completion.LightModelService.handleSuggestion(Editor) -[CALLS]-> fr.baretto.ollamassist.completion.LightModelService.handleBasicSugg [...]

=== AnAction [Class] ===
Inheritance paths:
  fr.baretto.ollamassist.completion.InlineCompletionAction -[EXTENDS]-> AnAction
  fr.baretto.ollamassist.chat.ui.menu.AddToContextAction -[EXTENDS]-> AnAction
  fr.baretto.ollamassist.actions.refactor.ApplyRefactoringAction -[EXTENDS]-> AnAction [...]

=== fr.baretto.ollamassist.setting.OllamAssistSettings.getAuthMode() [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.auth.AuthMode
Graph paths:
  fr.baretto.ollamassist.setting.OllamAssistSettings.getAuthMode() -[CALLS]-> fr.baretto.ollamassist.setting.OllamaSettings.getInstance()

=== fr.baretto.ollamassist.setting.ConfigurationPanel.getAuthMode() [Function] ===
Visibility: public
Returns: fr.baretto.ollamassist.auth.AuthMode
Graph paths:
  fr.baretto.ollamassist.setting.OllamassistSettingsConfigurable.isModified() -[CALLS]-> fr.baretto.ollamassist.setting.ConfigurationPanel.getAuthMode() [...]'''

CTX_NEO4J_INGEST = '''\
=== fr.baretto.ollamassist.chat.rag.DocumentIngestFactory [Class] ===
Visibility: public
Annotations:
  - Slf4j
  - NoArgsConstructor
  - Getter
Fields:
  - private FALLBACK_EMBEDDING_MODEL

=== fr.baretto.ollamassist.chat.rag.DocumentIngestFactory.create(EmbeddingStore<TextSegment>,Project) [Function] ===
Visibility: public
Returns: EmbeddingStoreIngestor
Parameters:
  - project: Project
  - store: EmbeddingStore<TextSegment>
Graph paths:
  fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline.handleCorruption() [...]

=== fr.baretto.ollamassist.setting.OllamaSettings [Class] ===
Visibility: public
Annotations:
  - State
Inheritance paths:
  fr.baretto.ollamassist.setting.OllamaSettings -[IMPLEMENTS]-> PersistentStateComponent<OllamaSettings.State>
Fields:
  - private myState
  - public DEFAULT_MODEL
  - public DEFAULT_URL

=== fr.baretto.ollamassist.codec.DefaultJsonCodecFactory.create() [Function] ===
Visibility: public
Returns: Json.JsonCodec
Annotations:
  - Override

=== fr.baretto.ollamassist.chat.service.OllamaService [Class] ===
Visibility: public
Annotations:
  - Service
  - Slf4j
Inheritance paths:
  fr.baretto.ollamassist.chat.service.OllamaService -[IMPLEMENTS]-> fr.baretto.ollamassist.setting.ModelListener
  fr.baretto.ollamassist.chat.service.OllamaService -[IMPLEMENTS]-> Disposable'''

# Contexte Lucene observé au niveau des en-têtes d'extraits uniquement.
CTX_LUCENE_CACHE = '''\
Method: fr.baretto.ollamassist.completion.SuggestionCache#generateCacheKey [...]

Method: fr.baretto.ollamassist.completion.EnhancedCompletionService#handleCompletionWithCache [...]

Type: class fr.baretto.ollamassist.completion.SuggestionCache [...]

Method: fr.baretto.ollamassist.completion.SuggestionCache#get [...]

Method: fr.baretto.ollamassist.completion.SuggestionCache#getStats [...]

Method: fr.baretto.ollamassist.completion.SuggestionCache#put [...]

Method: fr.baretto.ollamassist.completion.CompletionDebouncer#getDebugInfo [...]

Type: class fr.baretto.ollamassist.completion.EnhancedCompletionService [...]

Type: class fr.baretto.ollamassist.completion.CompletionDebouncer [...]

Type: class fr.baretto.ollamassist.completion.CachedSuggestion [...]'''

CTX_LUCENE_PREREQ = '''\
Method: fr.baretto.ollamassist.prerequiste.PrerequisiteService#checkLocalEmbeddingModel [...]

Method: fr.baretto.ollamassist.prerequiste.PrerequisiteService#checkEmbeddingModelAsync [...]

Method: fr.baretto.ollamassist.chat.rag.DocumentIngestFactory#createEmbeddingModel [...]

Type: class fr.baretto.ollamassist.prerequiste.EmbeddingModelCheckResult [...]

Method: fr.baretto.ollamassist.prerequiste.EmbeddingModelCheckResult#localAvailable [...]

Method: fr.baretto.ollamassist.prerequiste.EmbeddingModelCheckResult#localFailedWithFallback [...]

Method: fr.baretto.ollamassist.prerequiste.EmbeddingModelCheckResult#ollamaAvailable [...]

Method: fr.baretto.ollamassist.prerequiste.PrerequisiteService#testDJLNativeLibraries [...]

Method: fr.baretto.ollamassist.utils.FontUtils#getIDECodeFont [...]

Method: fr.baretto.ollamassist.prerequiste.PrerequisitesPanel#checkPrerequisitesAsync [...]'''

CTX_LUCENE_STORE = '''\
Method: fr.baretto.ollamassist.completion.SuggestionActionHandler#isEnabledForCaret [...]

Type: interface fr.baretto.ollamassist.notification.core.NotificationStorage [...]

Type: class fr.baretto.ollamassist.agent.tools.ApprovalTimeoutException extends RuntimeException [...]

Method: fr.baretto.ollamassist.setting.ConfigurationPanel#isToolsEnabled [...]

Method: fr.baretto.ollamassist.completion.MultiSuggestionManager#displayCurrentSuggestion [...]

Type: class fr.baretto.ollamassist.chat.service.OllamaService implements Disposable, ModelListener [...]

Type: class fr.baretto.ollamassist.notification.storage.PersistentNotificationStorage implements NotificationStorage [...]'''

# ══ RAG_CONTEXT_RELEVANCE (7) ════════════════════════════════════════════════

add(example(
    meta={"id": "b13-001", "famille": "rag-ctx-pipeline-reessais-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_NEO4J_PIPELINE,
    requete="How does DocumentIndexingPipeline handle document errors and retries?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête porte sur le traitement des erreurs et des réessais dans `DocumentIndexingPipeline`. Le contexte fournit le nœud de classe `DocumentIndexingPipeline` avec sa liste de champs, dont `fileRetries` et `PROCESSING_ERROR_FORMAT`, puis `CorruptedIndexException -[EXTENDS]-> RuntimeException`, `IndexRegistry.isIndexed(String)` et `EditorListener.handleEditorRelease(Editor)`.
2. Vérification point par point : la classe visée est présente et deux de ses champs touchent directement au sujet, `fileRetries` pour les réessais et `PROCESSING_ERROR_FORMAT` pour les erreurs ; `CorruptedIndexException` relève du même domaine. La pertinence est donc établie. La suffisance ne l'est pas : aucun nœud de fonction de cette classe ne figure dans le contexte, donc rien sur la méthode qui traite l'erreur, rien sur le nombre de réessais — le nom `fileRetries` indique qu'un compteur existe, pas sa valeur ni sa politique. Répondre exigerait d'inventer le mécanisme. Le bruit reste maîtrisé : deux extraits hors sujet sur cinq, courts, et sans risque de confusion avec la classe visée.
3. Synthèse : la bonne classe est là, mais le contexte ne contient que sa structure, pas le comportement demandé. FAIL.
''',
    reason="Le nœud de classe montre le champ fileRetries mais aucun corps ni aucune fonction : la politique de réessai reste absente.",
))

add(example(
    meta={"id": "b13-002", "famille": "rag-ctx-bracketparser-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_NEO4J_PARSER,
    requete="What does BracketCallParser parse from LLM output?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : le contexte contient le nœud de classe `BracketCallParser`, qui implémente `ToolCallParser` et déclare les champs `BRACKET_PATTERN` et `MAX_ARGUMENTS`, ainsi que deux nœuds de fonction `parse(String)` — celui de l'interface et celui de l'implémentation, annoté `@Override` — tous deux renvoyant `Optional<DetectedToolCall>`.
2. Vérification point par point : la classe et la méthode visées sont directement présentes, donc le contexte est pertinent. Sur la suffisance, l'ensemble permet de répondre à la question posée : la classe analyse un texte et en extrait éventuellement un appel d'outil, le type `Optional<DetectedToolCall>` disant à la fois la nature du résultat et son caractère facultatif, le champ `BRACKET_PATTERN` indiquant une reconnaissance par motif entre crochets, et `MAX_ARGUMENTS` une limite sur les arguments. L'arête depuis `ToolCallDetector.detect(String)` situe l'appelant. Les deux derniers extraits, un type générique de liste et `LogCellRenderer`, sont du bruit, mais brefs et arrivant en fin de contexte.
3. Synthèse : la classe, sa méthode, son type de retour et ses champs structurants sont tous présents. PASS.
''',
    reason="Les nœuds de classe et de fonction donnent la méthode parse, son type Optional<DetectedToolCall> et les champs BRACKET_PATTERN et MAX_ARGUMENTS.",
))

add(example(
    meta={"id": "b13-003", "famille": "rag-ctx-assistant-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_NEO4J_ASSISTANT,
    requete="What methods does the Assistant interface define?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": False, "contexte_suffisant": False, "bruit_maitrise": False},
    thinking='''
1. Énumération des éléments clés : la requête porte sur l'interface `Assistant` et sur les méthodes qu'elle déclare. Le contexte fournit `ConversationMessage.assistant(String)`, `LightModelService.handleSuggestion(Editor)`, le nœud `AnAction` avec ses classes héritières, et deux fonctions `getAuthMode()`.
2. Vérification point par point : l'interface `Assistant` **n'apparaît dans aucun extrait**. Le premier est une méthode de fabrique nommée `assistant` sur une classe de message, homonyme mais sans rapport avec l'interface visée ; les autres portent sur la complétion, les actions IntelliJ et les réglages d'authentification. Le contexte n'est donc ni pertinent ni suffisant, et le bruit est total. Ce cas mérite attention pour une autre raison : une mesure automatique de couverture d'indices, cherchant les sous-chaînes attendues, donne ici un score élevé — le mot « assistant » apparaît, les autres termes attendus se retrouvent par hasard dans des extraits voisins. Cette couverture est trompeuse et ne doit jamais tenir lieu de jugement de suffisance : seule la lecture des extraits établit que l'interface demandée est absente.
3. Synthèse : l'interface visée ne figure pas dans le contexte, dont les extraits ne sont reliés à la requête que par homonymie. FAIL.
''',
    reason="L'interface Assistant est absente : le seul extrait proche est ConversationMessage.assistant(String), un homonyme sans rapport.",
))

add(example(
    meta={"id": "b13-004", "famille": "rag-ctx-cache-cles-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_LUCENE_CACHE,
    requete="How does SuggestionCache generate cache keys for completion requests?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête vise la construction des clés de cache par `SuggestionCache`. Le premier extrait est précisément `SuggestionCache#generateCacheKey`, suivi de la classe `SuggestionCache` elle-même et de ses autres méthodes `get`, `put` et `getStats`, puis de classes voisines du même paquet de complétion.
2. Vérification point par point : la méthode exactement demandée occupe la première place du contexte, la pertinence est donc immédiate. Sur la suffisance, en revanche, le contexte ne porte que des signatures : les dix extraits sont tronqués et **aucun corps de méthode n'y figure**. Or la requête demande *comment* la clé est construite, ce qu'un nom de méthode ne dit pas. `generateCacheKey` annonce l'intention sans livrer la composition — quels champs entrent dans la clé, dans quel ordre, avec quel séparateur ou quelle fonction de hachage. La différence avec un contexte suffisant se mesure sur `b13-007`, où les noms `localAvailable`, `localFailedWithFallback` et `ollamaAvailable` décrivent à eux seuls la logique interrogée ; ici, rien de tel. Le bruit reste maîtrisé, sept extraits sur dix portant sur le cache.
3. Synthèse : la méthode visée est en tête de contexte, mais le contexte ne contient que des signatures et ne permet pas de dire comment la clé est construite. FAIL.
''',
    reason="generateCacheKey est en tête de contexte, mais aucun corps de méthode n'est fourni : la construction de la clé reste indéterminable.",
))

add(example(
    meta={"id": "b13-005", "famille": "rag-ctx-store-interfaces-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_LUCENE_STORE,
    requete="What does LuceneEmbeddingStore implement?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": False, "contexte_suffisant": False, "bruit_maitrise": False},
    thinking='''
1. Énumération des éléments clés : la requête porte sur les interfaces implémentées par `LuceneEmbeddingStore`. Les extraits couvrent `SuggestionActionHandler#isEnabledForCaret`, l'interface `NotificationStorage`, `ApprovalTimeoutException`, `ConfigurationPanel#isToolsEnabled`, `MultiSuggestionManager#displayCurrentSuggestion`, `OllamaService implements Disposable, ModelListener` et `PersistentNotificationStorage implements NotificationStorage`.
2. Vérification point par point : `LuceneEmbeddingStore` **n'apparaît dans aucun extrait**. Le contexte est donc hors sujet, et il est trompeur d'une manière particulière : deux extraits sont des déclarations d'implémentation d'interface, donc de la bonne **forme** grammaticale, mais portant sur `OllamaService` et `PersistentNotificationStorage`. Une lecture superficielle pourrait en tirer une réponse comme `Disposable, ModelListener`, qui serait fausse. Ni la pertinence ni la suffisance ne sont atteintes, et le bruit occupe la totalité du contexte.
3. Synthèse : la classe interrogée est absente, et les extraits de forme adéquate portent sur d'autres types. FAIL.
''',
    reason="LuceneEmbeddingStore n'apparaît nulle part ; les déclarations d'implémentation présentes concernent OllamaService et PersistentNotificationStorage.",
))

add(example(
    meta={"id": "b13-006", "famille": "rag-ctx-ingest-fallback-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "limite", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_NEO4J_INGEST,
    requete="How does DocumentIngestFactory create the embedding model with DJL fallback to Ollama?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête porte sur `createEmbeddingModel` et sur le repli de DJL vers Ollama. Le contexte donne le nœud de classe `DocumentIngestFactory`, avec le champ `FALLBACK_EMBEDDING_MODEL`, puis la fonction `create(EmbeddingStore<TextSegment>, Project)`, et trois extraits sur `OllamaSettings`, `DefaultJsonCodecFactory` et `OllamaService`.
2. Vérification point par point : la classe visée est présente et le champ `FALLBACK_EMBEDDING_MODEL` touche directement au sujet du repli, donc la pertinence est acquise. La suffisance ne l'est pas : la fonction demandée, `createEmbeddingModel`, ne figure pas dans le contexte — seule `create(...)`, de signature et de rôle différents, est fournie. Rien ne montre le modèle DJL, ni l'exception qui déclenche le repli, ni le modèle Ollama de remplacement. Le nom du champ **suggère** un repli sans en révéler le mécanisme ; c'est précisément le genre d'indice qui invite à extrapoler. Le bruit reste maîtrisé, les trois extraits hors sujet étant courts et clairement identifiés.
3. Synthèse : le contexte est authentiquement pertinent et nomme le repli, mais la fonction interrogée en est absente, donc il ne permet pas de répondre. FAIL.
''',
    reason="Le champ FALLBACK_EMBEDDING_MODEL évoque le repli, mais createEmbeddingModel est absente : seule create(...) figure au contexte.",
))

add(example(
    meta={"id": "b13-007", "famille": "rag-ctx-prerequis-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_LUCENE_PREREQ,
    requete="How does PrerequisiteService fall back from local DJL embedding to Ollama?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête porte sur le repli du modèle d'embedding local DJL vers Ollama dans `PrerequisiteService`. Les extraits fournissent `checkLocalEmbeddingModel`, `checkEmbeddingModelAsync`, `DocumentIngestFactory#createEmbeddingModel`, la classe `EmbeddingModelCheckResult` et ses trois méthodes `localAvailable`, `localFailedWithFallback` et `ollamaAvailable`, ainsi que `testDJLNativeLibraries`.
2. Vérification point par point : les deux méthodes nommées dans la requête sont présentes, la pertinence est immédiate. Sur la suffisance, le contexte couvre la chaîne complète : le test des bibliothèques natives DJL, la vérification du modèle local, l'orchestration asynchrone, et surtout le type de résultat dont les trois cas — local disponible, échec local avec repli, Ollama disponible — décrivent exactement la logique demandée. Le nom `localFailedWithFallback` porte à lui seul la réponse. Le contexte est verbeux, dix extraits dont plusieurs accesseurs redondants et un `FontUtils#getIDECodeFont` sans aucun rapport, mais cette abondance ne noie pas l'information utile : les huit premiers extraits sont tous du domaine visé, et le seul extrait parasite arrive en neuvième position.
3. Synthèse : contexte long mais dense, couvrant toute la chaîne de repli interrogée. PASS.
''',
    reason="La chaîne complète est couverte, de testDJLNativeLibraries à localFailedWithFallback ; la verbosité ne noie pas l'information utile.",
))

# ══ RAG_FAITHFULNESS (8) ═════════════════════════════════════════════════════

add(example(
    meta={"id": "b13-008", "famille": "rag-ctx-pipeline-reessais-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": True, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_PIPELINE,
    requete="How does DocumentIndexingPipeline handle document errors and retries?",
    reponse='''
## Le mécanisme de réessai

`DocumentIndexingPipeline` maintient un compteur par fichier dans le champ `fileRetries`. Lorsqu'un document échoue, la méthode `handleDocumentError` le replace **en tête** de la file de traitement et incrémente son compteur.

Le document est réessayé jusqu'à **trois fois** — la constante `MAX_RETRIES` vaut 3 — après quoi il est définitivement abandonné et le traitement passe au suivant.

## Le cas de l'index corrompu

Si l'exception rencontrée est une `CorruptedIndexException`, le pipeline ne réessaie pas : il déclenche `handleCorruption()`, qui reconstruit l'index depuis zéro.

## Traitement par lots

Le pipeline traite les documents par lots de 10 en mode asynchrone, et de 100 en mode synchrone.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte contient le nœud de classe `DocumentIndexingPipeline` avec sa liste de champs — dont `fileRetries`, `isRunning`, `scheduler`, `PROCESSING_ERROR_FORMAT` — le nœud `CorruptedIndexException -[EXTENDS]-> RuntimeException`, la fonction `IndexRegistry.isIndexed(String)` et une fonction d'`EditorListener`. Aucun corps de méthode, aucune constante avec sa valeur.
2. Vérification point par point : seule l'existence du champ `fileRetries` et celle de `CorruptedIndexException` sont étayées. Tout le reste est absent du contexte : la méthode `handleDocumentError` n'y figure pas, la remise en tête de file non plus, la constante `MAX_RETRIES` et sa valeur de 3 encore moins — le contexte ne contient aucune constante de ce nom, et un nœud de classe ne porte jamais les valeurs. Les tailles de lot, 10 et 100, sortent de nulle part. L'appel à `handleCorruption()` apparaît bien ailleurs dans le corpus, mais pas dans les extraits fournis ici. Ces affirmations se trouvent être exactes pour la codebase réelle, ce qui ne change rien : sous cette tâche, une affirmation non étayée par le contexte doit être rejetée, faute de quoi le juge ne saurait plus distinguer une restitution d'une hallucination. La précision des chiffres avancés aggrave le défaut plutôt qu'elle ne le crédibilise.
3. Synthèse : au-delà de deux noms, la sortie décrit un mécanisme et des valeurs entièrement absents du contexte. FAIL.
''',
    reason="handleDocumentError, MAX_RETRIES = 3 et les tailles de lot n'apparaissent nulle part dans un contexte fait de nœuds sans corps.",
))

add(example(
    meta={"id": "b13-009", "famille": "rag-ctx-pipeline-reessais-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_PIPELINE,
    requete="How does DocumentIndexingPipeline handle document errors and retries?",
    reponse='''
Le contexte ne permet qu'une réponse partielle.

Ce qu'il établit : la classe `DocumentIndexingPipeline` déclare un champ `fileRetries`, dont le nom indique un suivi des réessais par fichier, ainsi qu'un champ `PROCESSING_ERROR_FORMAT`, vraisemblablement un gabarit de message d'erreur, et un `scheduler`. Le contexte contient par ailleurs une exception dédiée, `CorruptedIndexException`, qui étend `RuntimeException`.

Ce qu'il n'établit pas : aucun corps de méthode n'est fourni, et aucune fonction de cette classe ne figure dans les extraits. Je ne peux donc pas dire combien de réessais sont effectués, dans quel ordre les documents sont remis en file, ni comment la corruption d'index est traitée — seule l'existence du type d'exception est visible.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte donne le nœud de classe avec sa liste de champs et le nœud `CorruptedIndexException -[EXTENDS]-> RuntimeException`, sans aucun corps ni aucune fonction de la classe interrogée.
2. Vérification point par point : chaque affirmation correspond à un élément présent. Les trois champs cités figurent dans la liste, et la relation d'héritage de l'exception est reprise exactement. Les interprétations tirées des noms sont explicitement marquées comme telles — « dont le nom indique », « vraisemblablement » — au lieu d'être présentées comme des faits, ce qui est la bonne façon de lire une liste de champs. Aucun symbole, aucune valeur, aucune méthode absente du contexte n'est introduit ; en particulier, aucun nombre de réessais n'est avancé. La seconde partie délimite explicitement les limites du contexte, en identifiant correctement la cause : l'absence de corps de méthode.
3. Synthèse : affirmations toutes étayées, inférences signalées comme telles, et lacunes du contexte explicitement posées. PASS.
''',
    reason="Ne retient que les champs et l'exception réellement présents, marque ses inférences et refuse d'avancer un nombre de réessais.",
))

add(example(
    meta={"id": "b13-010", "famille": "rag-ctx-bracketparser-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_PARSER,
    requete="What does BracketCallParser parse from LLM output?",
    reponse='''
## Le format reconnu

`BracketCallParser` reconnaît le format `[CALL CreateFile('chemin', 'contenu')]` dans la sortie du modèle. Il s'agit de la seule commande prise en charge : le parseur ne gère que `CreateFile`, et renvoie un `Optional` vide pour toute autre forme.

## Sa place dans le dispositif

La classe implémente `ToolCallParser` et redéfinit `parse(String)`, comme l'indique l'annotation `@Override`. Le type de retour, `Optional<DetectedToolCall>`, encode directement le fait qu'une analyse puisse ne rien trouver : pas de valeur sentinelle, pas de `null` à tester chez l'appelant. L'appelant en question est `ToolCallDetector.detect(String)`, qui interroge les parseurs dont il dispose.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit le nœud de classe `BracketCallParser`, implémentant `ToolCallParser`, avec les champs `BRACKET_PATTERN` et `MAX_ARGUMENTS`, ainsi que les deux nœuds `parse(String)` renvoyant `Optional<DetectedToolCall>`.
2. Vérification point par point : la seconde section est solidement ancrée — l'arête `IMPLEMENTS` vers `ToolCallParser`, l'annotation `@Override`, le type de retour `Optional<DetectedToolCall>` et l'appelant `ToolCallDetector.detect(String)` figurent tels quels dans les extraits, et la lecture qui en est faite est juste. La première ne l'est pas. La syntaxe exacte `[CALL CreateFile('chemin', 'contenu')]` n'apparaît nulle part : le contexte nomme un champ de motif sans en donner la valeur. Surtout, l'affirmation selon laquelle `CreateFile` serait la **seule** commande prise en charge est une restriction que rien ne soutient — le contexte ne mentionne jamais `CreateFile`, et le champ `MAX_ARGUMENTS` suggère au contraire un format paramétrable. Cette affirmation se trouve être exacte dans la codebase, mais elle ne peut pas être lue dans les extraits fournis : sous cette tâche, elle doit être rejetée. Une portée annoncée à tort comme exhaustive est d'ailleurs le type d'erreur le plus coûteux, puisqu'elle ferme la question.
3. Synthèse : la syntaxe citée et la restriction à une commande unique sont absentes du contexte, qui ne donne ni la valeur du motif ni aucun nom de commande. FAIL.
''',
    reason="Ni la syntaxe [CALL CreateFile(...)] ni la restriction à cette seule commande ne figurent au contexte, qui ne donne pas la valeur de BRACKET_PATTERN.",
))

add(example(
    meta={"id": "b13-011", "famille": "rag-ctx-bracketparser-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_PARSER,
    requete="What does BracketCallParser parse from LLM output?",
    reponse='''
## Ce que le contexte établit

D'après le contexte :

- `BracketCallParser` implémente l'interface `ToolCallParser` et redéfinit sa méthode `parse(String text)`, comme l'indique l'annotation `@Override`.
- Cette méthode renvoie un `Optional<DetectedToolCall>` : l'analyse peut donc ne rien détecter, auquel cas l'`Optional` est vide.
- La classe déclare deux champs, `BRACKET_PATTERN` et `MAX_ARGUMENTS`, dont les noms suggèrent une reconnaissance par expression régulière entre crochets et une limite sur le nombre d'arguments acceptés.
- L'appelant visible est `ToolCallDetector.detect(String)`.

## Ce qu'il ne permet pas de dire

La valeur du motif n'est pas fournie, donc la syntaxe exacte reconnue et les commandes acceptées ne sont pas déterminables à partir de ce contexte.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte donne l'arête `IMPLEMENTS` vers `ToolCallParser`, les deux nœuds `parse(String)` avec le type de retour `Optional<DetectedToolCall>` et l'annotation `@Override`, les champs `BRACKET_PATTERN` et `MAX_ARGUMENTS`, et l'arête `CALLS` depuis `ToolCallDetector.detect(String)`.
2. Vérification point par point : les quatre affirmations correspondent chacune à un élément explicite. La lecture de l'`Optional` vide est une déduction directe de la sémantique du type, et la lecture des noms de champs est prudemment introduite par « dont les noms suggèrent », sans affirmer ni la syntaxe ni la limite. Aucun nom de commande n'est avancé. Le dernier paragraphe identifie correctement la limite décisive du contexte, l'absence de la valeur du motif, et en tire la bonne conséquence sur ce qui reste indéterminable.
3. Synthèse : affirmations étayées, inférences signalées, et frontière du contexte explicitement tracée là où elle passe. PASS.
''',
    reason="S'en tient aux arêtes et champs présents, marque ses inférences et constate que la valeur du motif manque pour conclure sur la syntaxe.",
))

add(example(
    meta={"id": "b13-012", "famille": "rag-ctx-assistant-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_ASSISTANT,
    requete="What methods does the Assistant interface define?",
    reponse='''
## Les méthodes

L'interface `Assistant` définit deux méthodes, toutes deux renvoyant un `TokenStream` :

- `chat(String systemPrompt, String message)` ;
- `refactor(String refactorPrompt, String code, String language)`.

## Le type de retour

Le type `TokenStream` permet de consommer la réponse du modèle au fil de sa génération. C'est ce qui rend possible l'affichage progressif dans la fenêtre de discussion : l'interface reçoit les jetons à mesure qu'ils arrivent, au lieu d'attendre la fin de la génération pour afficher un bloc complet.

## Le découpage des paramètres

Séparer l'invite système du message utilisateur, plutôt que de les concaténer, laisse la couche d'infrastructure décider du gabarit exact attendu par le modèle.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit `ConversationMessage.assistant(String)`, `LightModelService.handleSuggestion(Editor)`, le nœud `AnAction` et deux fonctions `getAuthMode()`. L'interface `Assistant` n'y figure pas.
2. Vérification point par point : aucune des deux méthodes citées n'apparaît dans les extraits, pas plus que le type `TokenStream`. La réponse décrit donc intégralement une interface absente du contexte fourni — et elle ne s'arrête pas aux signatures : l'affichage progressif et la séparation de l'invite système sont deux développements dont pas un mot ne figure au contexte. Le détail ajouté est ici l'inverse d'une garantie : plus la description s'étoffe, plus elle s'éloigne de ce que les extraits permettent d'affirmer. Ces signatures sont exactes dans la codebase réelle, et c'est précisément ce qui rend le cas instructif : la sortie est juste, et doit malgré tout être rejetée, puisque rien dans le contexte ne la soutient. Accepter une réponse parce qu'elle sonne vrai revient à évaluer sa propre connaissance du sujet, pas l'ancrage de la réponse — et sur un contexte où la vérité diffère, le même jugement laisserait passer une invention. Le seul élément du contexte phonétiquement proche, `ConversationMessage.assistant(String)`, est une méthode de fabrique sans rapport, que la sortie ne mentionne d'ailleurs pas. Aucune citation n'est déformée, la sortie n'en fait aucune.
3. Synthèse : la réponse décrit une interface qui ne figure nulle part dans le contexte, ses deux signatures étant introuvables dans les extraits. FAIL.
''',
    reason="Les signatures chat et refactor, et le type TokenStream, sont absents du contexte : l'interface Assistant n'y figure pas du tout.",
))

add(example(
    meta={"id": "b13-013", "famille": "rag-ctx-assistant-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "limite", "verbeux": True, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_ASSISTANT,
    requete="What methods does the Assistant interface define?",
    reponse='''
## Réponse courte

Le contexte fourni ne contient pas l'interface `Assistant`. Je ne peux donc pas énumérer ses méthodes.

## Ce que contient réellement le contexte

Les cinq extraits portent sur des éléments distincts :

- `ConversationMessage.assistant(String)` — une méthode de fabrique construisant un message de conversation. Le nom est proche, mais il s'agit d'une classe de message, pas de l'interface interrogée.
- `LightModelService.handleSuggestion(Editor)` — relève de la complétion de code.
- `AnAction` — le nœud d'une classe IntelliJ, avec la liste des actions du projet qui en héritent.
- Deux fonctions `getAuthMode()`, qui concernent les réglages d'authentification.

## Pourquoi je m'arrête là

Répondre supposerait de restituer une interface que je n'ai pas sous les yeux. Le seul extrait dont le nom évoque la requête est un homonyme, et s'en servir produirait une réponse fausse avec l'apparence d'un ancrage.

Il faudrait relancer la recherche sur le nœud de l'interface elle-même pour obtenir ses méthodes.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte contient `ConversationMessage.assistant(String)`, `LightModelService.handleSuggestion(Editor)`, le nœud `AnAction` et deux `getAuthMode()`.
2. Vérification point par point : l'inventaire dressé par la sortie correspond exactement aux cinq extraits, sans omission ni ajout. Le constat central — l'absence de l'interface `Assistant` — est vérifiable et exact. L'identification de `ConversationMessage.assistant(String)` comme homonyme trompeur est juste et constitue le point important : c'est le seul extrait susceptible d'induire une réponse fabriquée. La sortie n'énonce aucune méthode de l'interface, donc n'invente rien, et ne déforme aucun extrait. Deux réserves de forme : la réponse est longue au regard de ce qu'elle établit, et elle ne répond pas à la question posée — mais cette seconde réserve n'est pas imputable à la sortie, le contexte ne le permettant pas.
3. Synthèse : la question reste sans réponse, mais tout ce qui est avancé est étayé, l'absence est correctement diagnostiquée et l'homonyme est explicitement écarté. PASS.
''',
    reason="Inventaire exact des extraits, absence de l'interface correctement constatée, et homonyme explicitement écarté au lieu d'être exploité.",
))

add(example(
    meta={"id": "b13-014", "famille": "rag-ctx-ingest-fallback-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_INGEST,
    requete="How does DocumentIngestFactory create the embedding model with DJL fallback to Ollama?",
    reponse='''
## Le mécanisme de repli

`DocumentIngestFactory.createEmbeddingModel()` tente d'abord d'instancier le modèle local `BgeSmallEnV15QuantizedEmbeddingModel`, fourni par DJL. Si le chargement des bibliothèques natives échoue — `UnsatisfiedLinkError` ou `ExceptionInInitializerError` — la fabrique se replie sur un `OllamaEmbeddingModel` configuré avec `nomic-embed-text`.

## Pourquoi ce repli existe

DJL embarque des bibliothèques natives dont la disponibilité dépend de la plateforme et de l'architecture. Sur un poste où elles ne se chargent pas, un modèle d'embarquement purement local devient inutilisable, et l'indexation échouerait entièrement. Le repli vers Ollama déporte le calcul vers un service externe, au prix d'un appel réseau par lot.

## Ce que la classe expose par ailleurs

`DocumentIngestFactory` déclare un champ `FALLBACK_EMBEDDING_MODEL`, et sa fonction publique est `create(EmbeddingStore<TextSegment>, Project)`, qui renvoie un `EmbeddingStoreIngestor` — l'objet chargé de découper, vectoriser et stocker les documents.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit le nœud de classe `DocumentIngestFactory`, ses annotations et son unique champ listé `FALLBACK_EMBEDDING_MODEL`, la fonction `create(EmbeddingStore<TextSegment>, Project)` renvoyant un `EmbeddingStoreIngestor`, puis trois extraits sans rapport direct.
2. Vérification point par point : la méthode `createEmbeddingModel()` dont parle la sortie **n'est pas dans le contexte** — seule `create(...)` y figure, avec une autre signature et un autre type de retour. Les deux classes de modèles citées, `BgeSmallEnV15QuantizedEmbeddingModel` et `OllamaEmbeddingModel`, sont absentes, de même que les deux types d'erreurs déclenchant le repli et le nom de modèle `nomic-embed-text`. Le seul appui réel est le champ `FALLBACK_EMBEDDING_MODEL`, dont le nom atteste qu'un repli existe — mais un nom de champ ne dit ni vers quoi l'on se replie, ni à quelle condition. La dernière section est en revanche exacte : la signature de `create(...)` et son type de retour figurent bien au contexte. Le texte mêle donc un ancrage réel à une invention, et l'ancrage se trouve précisément dans la partie que la question ne posait pas. La description est exacte au regard de la codebase, et c'est une circonstance aggravante ici : elle donne à un contenu non ancré toutes les apparences d'une lecture attentive du contexte.
3. Synthèse : méthode, classes de modèles et conditions de repli sont toutes absentes du contexte, qui n'en porte qu'un indice par le nom d'un champ. FAIL.
''',
    reason="createEmbeddingModel, les deux classes de modèles et les erreurs déclenchant le repli sont absentes ; seul le nom d'un champ évoque un repli.",
))

add(example(
    meta={"id": "b13-015", "famille": "rag-ctx-ingest-fallback-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "limite", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_INGEST,
    requete="How does DocumentIngestFactory create the embedding model with DJL fallback to Ollama?",
    reponse='''
Le contexte ne contient pas la méthode visée et ne permet pas de décrire le repli.

Ce qu'il montre : `DocumentIngestFactory` est une classe publique annotée `@Slf4j`, `@NoArgsConstructor` et `@Getter`, qui déclare un champ `FALLBACK_EMBEDDING_MODEL` — le nom atteste qu'un modèle de repli est prévu. La seule fonction fournie est `create(EmbeddingStore<TextSegment>, Project)`, qui renvoie un `EmbeddingStoreIngestor` et apparaît dans un chemin d'appel avec `DocumentIndexingPipeline.handleCorruption()`.

Ce qu'il ne montre pas : la méthode `createEmbeddingModel` n'est pas dans les extraits, pas plus que le nom du modèle DJL, celui du modèle Ollama, ou la condition déclenchant la bascule. Le champ de repli en établit l'existence, rien de plus.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte donne le nœud de classe avec ses trois annotations et le champ `FALLBACK_EMBEDDING_MODEL`, ainsi que la fonction `create(EmbeddingStore<TextSegment>, Project)` renvoyant `EmbeddingStoreIngestor`, avec un chemin d'appel impliquant `DocumentIndexingPipeline.handleCorruption()`.
2. Vérification point par point : chaque élément avancé figure dans les extraits, annotations et signature comprises, et le chemin d'appel est repris fidèlement. La lecture du champ est correctement bornée : la sortie dit que le nom atteste l'existence d'un repli, et explicite ensuite que cela ne dit ni la cible ni la condition — c'est exactement la limite de ce qu'autorise une liste de champs. Aucune classe de modèle, aucun type d'erreur, aucun nom de modèle n'est introduit. La délimitation finale est juste et nomme précisément l'absence décisive, celle de `createEmbeddingModel`.
3. Synthèse : la question posée reste sans réponse, mais chaque affirmation est étayée, l'inférence tirée du nom de champ est explicitement bornée, et l'absence décisive est identifiée. PASS.
''',
    reason="Tout est tiré des extraits, l'inférence sur FALLBACK_EMBEDDING_MODEL est bornée à l'existence d'un repli, et l'absence de createEmbeddingModel est nommée.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
