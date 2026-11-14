#!/usr/bin/env python3
"""Builds judge-finetune/data/seed/batch_12.jsonl (15 examples, premières tâches RAG).

Tous les contextes sont des récupérations RÉELLES, extraites le 2026-09-14 par
verification/ExtractRagContexts.java sur OllamAssist/src/main/java (162 fichiers) :
  - contextes-lucene-clean.jsonl  (preset hybrid,       10 extraits/question)
  - contextes-neo4j-clean.jsonl   (preset hybrid-graph,  5 extraits/question)

Les extraits sont recopiés tels quels. Là où l'extraction a été tronquée à la lecture,
le marqueur [...] le signale — la troncature est elle-même un comportement authentique.

Convention pour RAG_CONTEXT_RELEVANCE : la sortie évaluée EST le contexte récupéré ;
la section « SORTIE À ÉVALUER » le rappelle explicitement.
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

# ── Contextes réels réutilisés ────────────────────────────────────────────────

CTX_NEO4J_AUTH = '''\
=== fr.baretto.ollamassist.chat.rag.ProjectFileListener.handleFileCreated(VirtualFileEvent) [Function] ===
Visibility: private
Returns: void
Parameters:
  - event: VirtualFileEvent
Graph paths:
  fr.baretto.ollamassist.chat.rag.ProjectFileListener.createFileListener() -[CALLS]-> fr.baretto.ollamassist.chat.rag.ProjectFileListener.handleFileCreated(VirtualFileEvent) [...]

=== fr.baretto.ollamassist.component.ScrollableEditorTextField.createEditor() [Function] ===
Visibility: protected
Returns: EditorEx
Annotations:
  - NotNull
  - Override

=== fr.baretto.ollamassist.chat.ui.ChatThread.setupErrorHandler() [Function] ===
Visibility: private
Returns: void
Graph paths:
  fr.baretto.ollamassist.chat.ui.ChatThread.setupTokenStreamHandlers() -[CALLS]-> fr.baretto.ollamassist.chat.ui.ChatThread.setupErrorHandler() [...]

=== fr.baretto.ollamassist.prerequiste.UrlHelper.validateUrl(String) [Function] ===
Visibility: public
Returns: void
Parameters:
  - url: String
Graph paths:
  fr.baretto.ollamassist.prerequiste.UrlHelper.normalizeUrl(String) -[CALLS]-> fr.baretto.ollamassist.prerequiste.UrlHelper.validateUrl(String)

=== fr.baretto.ollamassist.chat.askfromcode.OllamaGutterIconRenderer.hashCode() [Function] ===
Visibility: public
Returns: int
Annotations:
  - Override
Graph paths:
  fr.baretto.ollamassist.chat.askfromcode.OllamaGutterIconRenderer.hashCode() -[CALLS]-> fr.baretto.ollamassist.chat.askfromcode.OllamaGutterIconRenderer.getIcon()'''

CTX_LUCENE_AUTH = '''\
AuthenticationHelper.java
package fr.baretto.ollamassist.auth;

import fr.baretto.ollamassist.setting.OllamaSettings;
import lombok.experimental.UtilityClass;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Map;

/**
 * Helper class for handling authentication for Ollama connections.
 *
 * <p>Supports two mutually exclusive schemes, selected by {@link AuthMode}:
 * HTTP Basic ({@code username:password}) and Bearer token / API key
 * (used by proxies such as OpenWebUI).</p>
 *
 * <p>All call sites must go through {@link #createAuthorizationHeaderValue()} or
 * {@link #authHeaders()} — the {@code Authorization} header value (including its scheme)
 * is buil [...]

Type: enum fr.baretto.ollamassist.auth.AuthMode
Doc: * Authentication mode used to reach the Ollama-compatible backend.
 *
 * <ul>
 *     <li>{@link #NONE} — no {@code Authorization} header is sent.</li>
 *     <li>{@link #BASIC} — HTTP Basic auth ({@code username:password}, Base64 encoded).</li>
 *     <li>{@link #BEARER} — Bearer token / API key (e.g. OpenWebUI proxy).</li>
 * </ul>
 *
 * Basic and Bearer are mutually exclusive: both rely on the single {@code Authorization} header.
Method: public static AuthMode fromString(String value)

Method: fr.baretto.ollamassist.prerequiste.PrerequisiteService#readAuthenticated [...]

Method: fr.baretto.ollamassist.chat.askfromcode.OllamaGutterIconRenderer#hashCode [...]'''

CTX_NEO4J_SERVICE = '''\
=== fr.baretto.ollamassist.chat.service.OllamaService [Class] ===
Visibility: public
Annotations:
  - Service
  - Slf4j
Inheritance paths:
  fr.baretto.ollamassist.chat.service.OllamaService -[IMPLEMENTS]-> fr.baretto.ollamassist.setting.ModelListener
  fr.baretto.ollamassist.chat.service.OllamaService -[IMPLEMENTS]-> Disposable
Fields:
  - private chatMemory
  - private messageBusConnection
  - p [...]

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

=== fr.baretto.ollamassist.chat.ui.OllamaMessage [Class] ===

=== fr.baretto.ollamassist.chat.ui.OllamaWindowFactory [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.ui.OllamaWindowFactory -[IMPLEMENTS]-> ToolWindowFactory
  fr.baretto.ollamassist.chat.ui.OllamaWindowFactory -[IMPLEMENTS]-> DumbAware

=== fr.baretto.ollamassist.chat.ui.OllamaContent [Class] ===
Visibility: public
Annotations:
  - Slf4j
Fields:
  - private agentRunning
  - private context [...]'''

CTX_LUCENE_SERVICE = '''\
Method: fr.baretto.ollamassist.setting.OllamaSettings#getInstance [...]

Method: fr.baretto.ollamassist.chat.ui.OllamaContent#createConversationPanel [...]

Method: fr.baretto.ollamassist.completion.SuggestionActionHandler#isEnabledForCaret [...]

Type: class fr.baretto.ollamassist.setting.OllamaSettings implements PersistentStateComponent [...]'''

CTX_NEO4J_RETRIEVE = '''\
=== fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.WorkspaceContextRetriever.get() [...]

=== fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) [Function] ===
Visibility: public
Returns: List<Content>
Annotations:
  - Override
Parameters:
  - query: Query
Graph paths:
  fr.baretto.ollamassist.chat.rag.HybridRetriever.retrieve(Query) -[CALLS]-> fr.baretto.ollamassist.chat.rag.HybridRetriever.safeGet(CompletableFuture<List<T>>) [...]

=== fr.baretto.ollamassist.chat.rag.ContextRetriever [Class] ===
Visibility: public
Inheritance paths:
  fr.baretto.ollamassist.chat.rag.ContextRetriever -[IMPLEMENTS]-> ContentRetriever
Fields:
  - private contentRetriever
  - private NOTIFICATION_GROUP_ID
  - private duckDuckGoContentRetriever
  - private workspaceContextProvider
  - private executor
  - private LAST_SOURCES
  - private settings

=== fr.baretto.ollamassist.chat.ui.Context [Class] ===

=== ContentRetriever [Class] ==='''

CTX_LUCENE_NOTIFIER = '''\
Type: interface fr.baretto.ollamassist.events.NewUserMessageNotifier
Field: Topic<NewUserMessageNotifier> TOPIC = Topic.create("New user message", NewUserMessageNotifier.class);
Method:  abstract void newUserMessage(String message)

Type: class fr.baretto.ollamassist.component.PluginNotifier [...]

Method: fr.baretto.ollamassist.events.NewUserMessageNotifier#newUserMessage
Signature:  abstract void newUserMessage(String message)

Method: fr.baretto.ollamassist.chat.ui.MessagesPanel#addUserMessage [...]'''

CTX_LUCENE_SEUIL = '''\
Type: class fr.baretto.ollamassist.agent.tools.ApprovalTimeoutException extends RuntimeException
Doc: * Thrown when the user does not respond to an approval request within the timeout.
     * Callers must surface this as a visible step failure rather than silently skipping
     * the operation.

Method: fr.baretto.ollamassist.component.LoadingListRenderer#getListCellRendererComponent
Signature: public Component getListCellRendererComponent(JList<?> list, Object value, int index, boolean isSelected, boolean cellHasFocus)
Body: {
    String displayValue = value != null ? value.toString() : "Loading...";
    FontMetrics metrics = getFontMetrics(getFont());
    int maxWidth = list.getFixedCellWidth() - 10; [...]

Type: class fr.baretto.ollamassist.setting.State [...]

Method: fr.baretto.ollamassist.setting.OllamaSettings#getApprovalTimeoutMinutes [...]

Method: fr.baretto.ollamassist.completion.MultiSuggestionManager#getCurrentSuggestionNumber [...]'''

# ══ RAG_CONTEXT_RELEVANCE (8) ════════════════════════════════════════════════

add(example(
    meta={"id": "b12-001", "famille": "rag-ctx-seuil-dynamique-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_LUCENE_SEUIL,
    requete="What does the calculateDynamicThreshold method compute in LuceneEmbeddingStore?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": False, "contexte_suffisant": False, "bruit_maitrise": False},
    thinking='''
1. Énumération des éléments clés : la requête porte sur la méthode `calculateDynamicThreshold` de la classe `LuceneEmbeddingStore`. Les extraits fournis concernent `ApprovalTimeoutException`, `LoadingListRenderer#getListCellRendererComponent`, la classe `State`, `OllamaSettings#getApprovalTimeoutMinutes` et `MultiSuggestionManager#getCurrentSuggestionNumber`.
2. Vérification point par point : aucun extrait ne mentionne `LuceneEmbeddingStore`, et aucun ne mentionne `calculateDynamicThreshold` — le contrôle de pertinence échoue donc dès le premier critère. Rien ne permet a fortiori de dire ce que la méthode calcule : le contexte est insuffisant. Quant au bruit, il n'est pas seulement présent, il occupe la totalité des extraits ; la seule parenté visible est lexicale, autour du mot « threshold » présent dans `getApprovalTimeoutMinutes` et dans la documentation du délai d'approbation, ce qui a vraisemblablement attiré la recherche vers un tout autre domaine fonctionnel.
3. Synthèse : le contexte ne contient rien de la classe ni de la méthode visées, et le bruit est total. FAIL.
''',
    reason="Aucun extrait ne mentionne LuceneEmbeddingStore ni calculateDynamicThreshold : la recherche a dérivé vers le délai d'approbation.",
))

add(example(
    meta={"id": "b12-002", "famille": "rag-ctx-ollamaservice-interfaces-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_NEO4J_SERVICE,
    requete="What interfaces does OllamaService implement?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête demande les interfaces implémentées par `OllamaService`. Le premier extrait est le nœud de classe `fr.baretto.ollamassist.chat.service.OllamaService`, avec deux arêtes d'héritage explicites : `-[IMPLEMENTS]-> fr.baretto.ollamassist.setting.ModelListener` et `-[IMPLEMENTS]-> Disposable`.
2. Vérification point par point : la classe visée est bien présente, donc le contexte est pertinent. Les deux arêtes `IMPLEMENTS` donnent la liste complète demandée, sans qu'il soit nécessaire de déduire quoi que ce soit : le contexte est suffisant pour répondre entièrement. Les quatre extraits suivants portent sur d'autres types — `OllamaSettings`, `OllamaMessage`, `OllamaWindowFactory`, `OllamaContent` — et constituent du bruit lexical autour du préfixe « Ollama ». Ce bruit reste maîtrisé : il vient après l'extrait utile, il est bref, et `OllamaSettings` ne peut pas être confondu avec `OllamaService` puisque son nœud porte son propre nom.
3. Synthèse : la réponse figure explicitement dans le premier extrait, et le bruit ne la noie pas. PASS.
''',
    reason="Le nœud OllamaService porte les deux arêtes IMPLEMENTS demandées ; le bruit sur le préfixe Ollama reste secondaire.",
))

add(example(
    meta={"id": "b12-003", "famille": "rag-ctx-auth-header-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_NEO4J_AUTH,
    requete="What authentication header does AuthenticationHelper generate?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": False, "contexte_suffisant": False, "bruit_maitrise": False},
    thinking='''
1. Énumération des éléments clés : la requête porte sur `AuthenticationHelper` et sur l'en-tête d'authentification qu'il produit. Les cinq extraits sont `ProjectFileListener.handleFileCreated`, `ScrollableEditorTextField.createEditor`, `ChatThread.setupErrorHandler`, `UrlHelper.validateUrl` et `OllamaGutterIconRenderer.hashCode`.
2. Vérification point par point : aucun des cinq ne concerne l'authentification, et `AuthenticationHelper` n'apparaît nulle part. Le contexte n'est donc ni pertinent ni suffisant. Le seul extrait qui pourrait donner le change est `UrlHelper.validateUrl`, du paquet `prerequiste`, qui touche à la connexion au serveur mais ne dit rien d'un en-tête : une pertinence apparente, pas réelle. Les cinq extraits étant hors sujet, le bruit n'est pas maîtrisé.
3. Synthèse : récupération entièrement à côté de la requête, sans même un extrait partiellement utile. FAIL.
''',
    reason="Les cinq extraits portent sur des fonctions sans lien avec l'authentification ; AuthenticationHelper est absent du contexte.",
))

add(example(
    meta={"id": "b12-004", "famille": "rag-ctx-auth-header-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "limite", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_LUCENE_AUTH,
    requete="What authentication header does AuthenticationHelper generate?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : le premier extrait est le fichier `AuthenticationHelper.java` lui-même, avec sa documentation ; le deuxième est l'énumération `AuthMode` et sa documentation détaillée. Suivent deux extraits sans rapport direct, `PrerequisiteService#readAuthenticated` et `OllamaGutterIconRenderer#hashCode`.
2. Vérification point par point : la classe visée est présente, le contexte est donc pertinent. Sur la suffisance, la documentation répond à la question posée : deux schémas mutuellement exclusifs sélectionnés par `AuthMode`, Basic avec `username:password` encodé en Base64, et Bearer pour un jeton ou une clé d'API, les deux reposant sur l'unique en-tête `Authorization`. La documentation nomme en outre les points d'entrée obligatoires, `createAuthorizationHeaderValue()` et `authHeaders()`. C'est suffisant pour répondre entièrement. Deux réserves : le premier extrait est tronqué en pleine phrase, ce qui prive du détail de construction de la valeur, et le dernier extrait est franchement hors sujet. Ni l'un ni l'autre n'empêche de répondre, et l'information utile occupe les deux premiers extraits.
3. Synthèse : la troncature et un extrait parasite ne suffisent pas à disqualifier un contexte qui contient la classe visée et la description complète des deux schémas. PASS.
''',
    reason="Le fichier AuthenticationHelper et l'énumération AuthMode répondent entièrement à la requête, malgré une troncature et un extrait parasite.",
))

add(example(
    meta={"id": "b12-005", "famille": "rag-ctx-ollamaservice-interfaces-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_LUCENE_SERVICE,
    requete="What interfaces does OllamaService implement?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": False, "contexte_suffisant": False, "bruit_maitrise": False},
    thinking='''
1. Énumération des éléments clés : la requête vise les interfaces de `OllamaService`. Les extraits portent sur `OllamaSettings#getInstance`, `OllamaContent#createConversationPanel`, `SuggestionActionHandler#isEnabledForCaret`, puis sur le type `OllamaSettings implements PersistentStateComponent`.
2. Vérification point par point : `OllamaService` est le seul symbole visé par la requête, et **il n'apparaît dans aucun extrait**. Le quatrième est bien une déclaration d'implémentation d'interface, ce qui donne au contexte la forme de la question, mais la classe déclarée y est `OllamaSettings` — un quasi-homonyme d'un paquet voisin, avec une interface sans rapport, `PersistentStateComponent`. Une ressemblance de forme sur la mauvaise classe n'est pas de la pertinence : aucun extrait ne porte sur le symbole interrogé. Le contexte est donc à la fois non pertinent et insuffisant, et le bruit est total puisque les quatre extraits sont hors sujet — il n'y a aucune information utile qu'ils pourraient noyer. Le danger est précisément là : ce contexte invite à répondre `PersistentStateComponent`, ce qui serait faux.
3. Synthèse : contexte de forme adéquate mais portant sur la mauvaise classe, donc insuffisant pour répondre. FAIL.
''',
    reason="Le seul extrait déclarant une interface concerne OllamaSettings, quasi-homonyme : OllamaService n'apparaît nulle part.",
))

add(example(
    meta={"id": "b12-006", "famille": "rag-ctx-notifier-lucene", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_LUCENE_NOTIFIER,
    requete="How does AskFromCodeAction notify the chat UI via NewUserMessageNotifier?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête porte sur deux entités et sur le lien entre elles — `AskFromCodeAction` d'une part, `NewUserMessageNotifier` d'autre part. Le contexte fournit l'interface `NewUserMessageNotifier` avec son champ `TOPIC` et sa méthode `newUserMessage(String)`, répétée dans un extrait ultérieur, plus `PluginNotifier` et `MessagesPanel#addUserMessage`.
2. Vérification point par point : la moitié de la question est couverte. Le mécanisme de notification est visible — un `Topic` IntelliJ et la méthode publiée — donc le contexte est pertinent. Mais `AskFromCodeAction` **n'apparaît dans aucun extrait**, si bien que rien ne montre qui publie sur ce sujet, ni à quel moment, ni avec quel contenu. Or la question porte précisément sur ce lien. Répondre exigerait de supposer le point de publication, c'est-à-dire d'inventer. Le bruit reste modéré et thématiquement proche, `PluginNotifier` et `MessagesPanel` relevant du même domaine d'affichage.
3. Synthèse : la cible de la notification est documentée, son émetteur est absent, donc le contexte ne permet pas de répondre à la question posée. FAIL.
''',
    reason="Le contexte documente NewUserMessageNotifier mais ne contient jamais AskFromCodeAction : le lien demandé est absent.",
))

add(example(
    meta={"id": "b12-007", "famille": "rag-ctx-contextretriever-retrieve-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_NEO4J_RETRIEVE,
    requete="What does the retrieve method do in ContextRetriever?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": True, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : le premier extrait est le nœud de fonction `ContextRetriever.retrieve(Query)`, public, renvoyant `List<Content>`, annoté `@Override`, avec une arête `CALLS` vers `WorkspaceContextRetriever.get()`. Le troisième extrait est le nœud de classe `ContextRetriever`, qui implémente `ContentRetriever` et porte les champs `contentRetriever`, `duckDuckGoContentRetriever`, `workspaceContextProvider` et `executor`.
2. Vérification point par point : la méthode visée est directement présente, le contexte est pertinent. Sur la suffisance, ces deux extraits donnent la signature, le type de retour, l'origine de l'annotation `@Override` par l'interface implémentée, et les collaborateurs — les champs nomment les trois sources de contexte et l'exécuteur, l'arête `CALLS` confirme l'appel à l'une d'elles. C'est assez pour décrire ce que fait la méthode. Deux extraits terminaux sont dégénérés, `Context [Class]` et `ContentRetriever [Class]` n'ayant aucun corps ; ils sont inutiles mais très courts et ne noient rien.
3. Synthèse : la méthode visée, sa signature et ses collaborateurs figurent dans le contexte, qui permet de répondre. PASS.
''',
    reason="Le nœud retrieve(Query) donne signature, type de retour et arête CALLS, et le nœud de classe nomme les trois sources de contexte.",
))

add(example(
    meta={"id": "b12-008", "famille": "rag-ctx-contextretriever-retrieve-neo4j", "task": "RAG_CONTEXT_RELEVANCE",
          "domaine": "rag", "tache": "retrieval", "cas": "limite", "verbeux": False, "langage": "java"},
    task="RAG_CONTEXT_RELEVANCE",
    contexte=CTX_NEO4J_RETRIEVE,
    requete="Which classes does ContextRetriever delegate to, and in what order are their results merged?",
    reponse=SORTIE_RELEVANCE,
    checks={"contexte_pertinent": True, "contexte_suffisant": False, "bruit_maitrise": True},
    thinking='''
1. Énumération des éléments clés : la requête comporte deux volets, la liste des classes déléguées et **l'ordre de fusion** de leurs résultats. Le contexte donne le nœud `ContextRetriever.retrieve(Query)` avec une arête `CALLS` vers `WorkspaceContextRetriever.get()`, le nœud de classe `ContextRetriever` avec ses champs `contentRetriever`, `duckDuckGoContentRetriever`, `workspaceContextProvider` et `executor`, ainsi que `HybridRetriever.retrieve(Query)`.
2. Vérification point par point : le premier volet est couvert, les champs et l'arête `CALLS` identifiant les collaborateurs. Le second ne l'est pas : le contexte expose la structure du graphe — qui appelle qui — mais aucun corps de méthode, donc rien sur la façon dont les résultats sont combinés, ni sur un ordre, une déduplication ou un filtrage. La présence du champ `executor` suggère un traitement concurrent, mais le déduire serait une inférence, pas une lecture. Le bruit reste maîtrisé, les deux nœuds vides étant très courts.
3. Synthèse : le contexte est nettement pertinent et répond à la moitié de la requête, mais l'ordre de fusion demandé n'y figure pas, et la suffisance porte sur la requête entière. FAIL.
''',
    reason="Les collaborateurs sont identifiables, mais aucun corps de méthode n'est fourni : l'ordre de fusion demandé reste absent du contexte.",
))

# ══ RAG_FAITHFULNESS (7) ═════════════════════════════════════════════════════

add(example(
    meta={"id": "b12-009", "famille": "rag-ctx-auth-header-lucene", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_LUCENE_AUTH,
    requete="What authentication header does AuthenticationHelper generate?",
    reponse='''
## Les modes disponibles

`AuthenticationHelper` gère l'authentification vers le service compatible Ollama, et le mode retenu est porté par l'énumération `AuthMode` :

- `NONE` — aucun en-tête `Authorization` n'est envoyé ;
- `BASIC` — authentification HTTP Basic, à partir du couple `username:password` ;
- `BEARER` — jeton ou clé d'API, tel qu'attendu par un mandataire comme OpenWebUI.

Les deux derniers sont mutuellement exclusifs, puisqu'ils reposent sur le même et unique en-tête `Authorization`.

## La génération de l'en-tête

`AuthenticationHelper` expose la méthode `createBasicAuthHeader(String username, String password)`, qui encode les identifiants en Base64 et renvoie la valeur de l'en-tête `Authorization` au format `Basic <identifiants encodés>`.

C'est cette méthode que les appelants utilisent pour authentifier leurs requêtes vers Ollama.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit le fichier `AuthenticationHelper.java` avec sa documentation, et l'énumération `AuthMode`. La documentation cite textuellement deux points d'entrée : « All call sites must go through {@link #createAuthorizationHeaderValue()} or {@link #authHeaders()} ». Elle décrit deux schémas mutuellement exclusifs, Basic avec `username:password` encodé en Base64, et Bearer.
2. Vérification point par point : la sortie affirme l'existence d'une méthode `createBasicAuthHeader(String, String)`. Ce nom **n'apparaît nulle part** dans le contexte fourni, qui nomme au contraire `createAuthorizationHeaderValue()` et `authHeaders()` comme les seuls points de passage autorisés. L'affirmation centrale n'est donc pas étayée, et la signature avancée est une invention : ni le nom, ni les paramètres, ni le type de retour ne figurent dans les extraits. Tout le reste de la réponse est pourtant solidement ancré — les trois modes de `AuthMode` et leur description, l'exclusivité mutuelle de Basic et Bearer, l'en-tête unique — et rien n'y est déformé : les citations restent exactes. C'est précisément cette proportion qui rend le cas difficile : un seul symbole inventé au milieu d'un texte par ailleurs fidèle, placé exactement là où se trouve la réponse à la question posée. À noter que la plausibilité de la réponse aggrave le défaut plutôt qu'elle ne l'excuse : un nom inventé mais vraisemblable est précisément ce qu'un juge doit rejeter.
3. Synthèse : la méthode centrale de la réponse est absente du contexte, qui désigne explicitement d'autres points d'entrée. FAIL.
''',
    reason="La méthode createBasicAuthHeader n'existe pas dans le contexte, qui impose au contraire createAuthorizationHeaderValue() ou authHeaders().",
))

add(example(
    meta={"id": "b12-010", "famille": "rag-ctx-auth-header-lucene", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_LUCENE_AUTH,
    requete="What authentication header does AuthenticationHelper generate?",
    reponse='''
D'après le contexte, `AuthenticationHelper` produit un unique en-tête `Authorization`, dont le schéma dépend de la valeur de `AuthMode` :

- `NONE` : aucun en-tête `Authorization` n'est envoyé ;
- `BASIC` : authentification HTTP Basic, à partir de `username:password` encodé en Base64 ;
- `BEARER` : jeton ou clé d'API, pour un mandataire tel qu'OpenWebUI.

Les deux schémas sont mutuellement exclusifs, puisqu'ils reposent sur le même en-tête. La documentation précise que tous les appelants doivent passer par `createAuthorizationHeaderValue()` ou `authHeaders()`.

Le détail de la construction de la valeur n'est pas visible : l'extrait est tronqué à cet endroit.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte contient la documentation de `AuthenticationHelper.java` et celle de l'énumération `AuthMode`, laquelle décrit `NONE`, `BASIC` et `BEARER`, et précise que Basic et Bearer sont mutuellement exclusifs car reposant sur l'unique en-tête `Authorization`.
2. Vérification point par point : chaque affirmation de la sortie se retrouve dans les extraits. Les trois modes et leur description viennent de la documentation de l'énumération, l'exclusivité mutuelle en est reprise presque mot pour mot, et les deux points d'entrée cités correspondent exactement à ceux nommés par la documentation du fichier. Aucun symbole, aucune signature ni aucun comportement absent du contexte n'est introduit — la réponse ne nomme notamment aucune méthode de construction interne. Les reprises sont fidèles, y compris la mention d'OpenWebUI comme exemple de mandataire. Point remarquable : la sortie signale explicitement que le détail de construction n'est pas visible du fait de la troncature, au lieu de le combler par déduction. C'est le comportement attendu en monde fermé.
3. Synthèse : toutes les affirmations sont étayées par le contexte, rien n'est inventé, et la limite du contexte est signalée plutôt que comblée. PASS.
''',
    reason="Chaque affirmation provient des extraits fournis, et la sortie signale la troncature au lieu de compléter par déduction.",
))

add(example(
    meta={"id": "b12-011", "famille": "rag-ctx-contextretriever-retrieve-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": True, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_RETRIEVE,
    requete="What does the retrieve method do in ContextRetriever?",
    reponse='''
## Vue d'ensemble

`ContextRetriever.retrieve(Query)` est le point d'entrée de la récupération de contexte. La méthode est publique, annotée `@Override`, et renvoie une `List<Content>`.

## Fonctionnement détaillé

La méthode lance **en parallèle, sur un pool de trois threads**, les trois sources de contexte dont dispose la classe : le `contentRetriever` interne adossé à l'index RAG, le `duckDuckGoContentRetriever` lorsque la recherche web est activée, et le `workspaceContextProvider`.

Les résultats sont ensuite fusionnés, avec **déduplication par texte** et **filtrage des extraits de moins de 30 caractères**, afin d'éviter de saturer la fenêtre de contexte avec des fragments inexploitables.

## Robustesse

L'ensemble est encadré par un délai d'attente, et les erreurs `InternalServerException` comme `TimeoutException` sont traitées explicitement pour qu'une source défaillante ne fasse pas échouer l'ensemble de la récupération.

## En résumé

Une agrégation concurrente de trois sources, robuste aux pannes partielles, avec nettoyage des résultats avant renvoi au modèle.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte contient le nœud de fonction `ContextRetriever.retrieve(Query)` — visibilité publique, retour `List<Content>`, annotation `@Override`, arête `CALLS` vers `WorkspaceContextRetriever.get()` — et le nœud de classe `ContextRetriever`, qui implémente `ContentRetriever` et déclare les champs `contentRetriever`, `duckDuckGoContentRetriever`, `workspaceContextProvider` et `executor`. Aucun corps de méthode n'est fourni.
2. Vérification point par point : le premier paragraphe est étayé, signature, visibilité, annotation et type de retour figurant tels quels dans le contexte. Tout le reste ne l'est pas. Le pool de **trois** threads, la **déduplication par texte**, le **filtrage à 30 caractères**, le délai d'attente et le traitement de `InternalServerException` et `TimeoutException` sont autant d'affirmations précises dont rien, dans les extraits, ne porte la trace : le contexte expose la structure du graphe, pas les corps. Le champ `executor` autorise à supposer un traitement concurrent, mais en déduire un pool de trois threads est une invention, et le chiffre de 30 caractères ne peut venir que d'une connaissance extérieure. C'est précisément le cas que cette tâche doit trancher : ces affirmations se trouvent être **vraies dans la codebase**, et doivent malgré tout être rejetées, puisque le contexte fourni ne les soutient pas. Un juge qui les accepterait au motif qu'elles sont exactes validerait, sur un autre dossier, une hallucination indiscernable. Les éléments effectivement repris du contexte ne sont en revanche pas déformés.
3. Synthèse : au-delà de la signature, la sortie décrit un comportement absent du contexte, dont le détail chiffré ne peut provenir que d'ailleurs. FAIL.
''',
    reason="Pool de trois threads, déduplication et filtrage à 30 caractères sont absents du contexte, qui ne contient aucun corps de méthode.",
))

add(example(
    meta={"id": "b12-012", "famille": "rag-ctx-contextretriever-retrieve-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_RETRIEVE,
    requete="What does the retrieve method do in ContextRetriever?",
    reponse='''
D'après le contexte fourni :

- `ContextRetriever.retrieve(Query)` est publique, annotée `@Override` et renvoie une `List<Content>`. L'annotation s'explique par le fait que `ContextRetriever` implémente `ContentRetriever`.
- Le graphe d'appels montre que la méthode appelle `WorkspaceContextRetriever.get()`.
- La classe déclare les champs `contentRetriever`, `duckDuckGoContentRetriever`, `workspaceContextProvider` et `executor`, ce qui indique plusieurs sources de contexte et la présence d'un exécuteur.

En revanche, le contexte ne contient aucun corps de méthode : il ne permet pas de dire comment les résultats de ces sources sont combinés, ni dans quel ordre, ni s'ils sont filtrés.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit le nœud de fonction `retrieve(Query)` avec sa visibilité, son type de retour `List<Content>`, son annotation `@Override` et son arête `CALLS` vers `WorkspaceContextRetriever.get()`, ainsi que le nœud de classe portant l'arête `IMPLEMENTS ContentRetriever` et la liste des champs.
2. Vérification point par point : chacune des trois affirmations correspond à un élément explicite du contexte. Le lien entre l'annotation `@Override` et l'interface implémentée est une déduction, mais une déduction dont les deux prémisses sont dans les extraits, et elle est présentée comme telle. La lecture des champs est prudente : la sortie dit qu'ils « indiquent » plusieurs sources et un exécuteur, sans affirmer un nombre de threads ni un mode de fusion. Aucun symbole absent des extraits n'est introduit, et rien n'est déformé. Le dernier paragraphe délimite explicitement ce que le contexte ne permet pas de conclure, ce qui est exactement la posture attendue.
3. Synthèse : affirmations toutes étayées, déductions signalées, et limites du contexte explicitement posées. PASS.
''',
    reason="Chaque élément est tiré des nœuds fournis, les déductions sont signalées, et l'absence de corps de méthode est explicitement relevée.",
))

add(example(
    meta={"id": "b12-013", "famille": "rag-ctx-ollamaservice-interfaces-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "parfait", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_SERVICE,
    requete="What interfaces does OllamaService implement?",
    reponse='''
Le contexte indique que `fr.baretto.ollamassist.chat.service.OllamaService` implémente deux interfaces :

- `fr.baretto.ollamassist.setting.ModelListener`
- `Disposable`

La classe est par ailleurs annotée `@Service` et `@Slf4j`.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le premier extrait est le nœud de classe `OllamaService`, avec ses annotations `Service` et `Slf4j`, et deux arêtes d'héritage `-[IMPLEMENTS]-> fr.baretto.ollamassist.setting.ModelListener` et `-[IMPLEMENTS]-> Disposable`.
2. Vérification point par point : les deux interfaces citées correspondent exactement aux deux arêtes, nom pleinement qualifié compris pour la première. Les deux annotations mentionnées figurent également dans l'extrait. La sortie s'en tient à ce que le contexte contient : elle n'ajoute aucune interface, ne commente pas le rôle de `Disposable` dans le cycle de vie d'IntelliJ, et ne tente pas de décrire ce que fait la classe. Elle ne se laisse pas non plus entraîner par l'extrait voisin sur `OllamaSettings implements PersistentStateComponent`, dont la proximité lexicale constituait le piège de ce contexte.
3. Synthèse : les deux interfaces et les annotations sont reprises fidèlement, sans ajout ni confusion avec la classe voisine. PASS.
''',
    reason="Les deux interfaces citées correspondent exactement aux arêtes IMPLEMENTS du nœud, sans confusion avec OllamaSettings.",
))

add(example(
    meta={"id": "b12-014", "famille": "rag-ctx-ollamaservice-interfaces-neo4j", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "defaillant", "verbeux": False, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_NEO4J_SERVICE,
    requete="What interfaces does OllamaService implement?",
    reponse='''
## Les interfaces

`OllamaService` implémente trois interfaces :

- `Disposable`, pour la libération des ressources à la fermeture du projet ;
- `ModelListener`, pour réagir aux changements de modèle ;
- `PersistentStateComponent`, qui lui permet de conserver sa configuration entre deux démarrages de l'IDE.

## Ce que le reste du nœud indique

Le nœud porte d'ailleurs l'arête `fr.baretto.ollamassist.chat.service.OllamaService -[IMPLEMENTS]-> PersistentStateComponent<OllamaService.State>`, ce qui confirme la troisième interface.

La classe porte deux annotations : `@Service`, qui en fait un composant géré par la plateforme et instancié à la demande, et `@Slf4j`, qui lui injecte un enregistreur de journaux.

Ses champs éclairent son rôle. `chatMemory` conserve l'historique de conversation, ce qui explique le besoin de persistance. `messageBusConnection` est la souscription au bus de messages d'IntelliJ — et c'est aussi ce qui rend `Disposable` nécessaire, une connexion au bus devant être libérée explicitement pour ne pas fuir à la fermeture du projet.

L'ensemble dessine un service à durée de vie longue, abonné à des événements et porteur d'un état à conserver.
''',
    checks={"affirmations_etayees": False, "absence_invention": False, "citations_exactes": False},
    thinking='''
1. Énumération des éléments clés : le nœud `OllamaService` porte exactement deux arêtes `IMPLEMENTS`, vers `fr.baretto.ollamassist.setting.ModelListener` et vers `Disposable`. Un extrait distinct montre `fr.baretto.ollamassist.setting.OllamaSettings -[IMPLEMENTS]-> PersistentStateComponent<OllamaSettings.State>`.
2. Vérification point par point : les deux premières interfaces citées sont étayées. La troisième ne l'est pas : `PersistentStateComponent` est rattachée par le contexte à `OllamaSettings`, une **autre classe**, et aucune arête ne la relie à `OllamaService`. La sortie attribue donc à une classe une interface qui appartient à sa voisine — exactement le piège que tendait ce contexte, où deux types au préfixe commun se suivent. Le dénombrement « trois interfaces » est faux pour la même raison. Plus grave, la sortie ne se contente pas d'attribuer : elle **fabrique une citation** à l'appui, en donnant pour une arête du nœud `OllamaService -[IMPLEMENTS]-> PersistentStateComponent<OllamaService.State>`, forme qui ne figure nulle part. L'arête réelle porte `OllamaSettings` des deux côtés, y compris dans le paramètre de type. Une attribution erronée devient ainsi une citation déformée, présentée comme une preuve tirée du contexte — c'est le degré au-dessus de l'invention simple, puisque le lecteur est invité à vérifier et croit trouver confirmation. Le reste de la réponse est en revanche correctement ancré : les annotations `@Service` et `@Slf4j` figurent bien au nœud, ainsi que les champs `chatMemory` et `messageBusConnection`. Le rattachement de `Disposable` à la libération de la connexion au bus est une déduction, mais une déduction dont les deux prémisses sont dans l'extrait. Les justifications fonctionnelles avancées pour chaque interface ne figurent pas davantage dans le contexte, mais elles restent secondaires face à l'erreur d'attribution et à la citation fabriquée qui la maquille en preuve.
3. Synthèse : une interface de plus est attribuée à la classe, en réalité portée par un type voisin du contexte. FAIL.
''',
    reason="PersistentStateComponent est rattachée par le contexte à OllamaSettings, et la citation produite à l'appui réécrit l'arête au nom d'OllamaService.",
))

add(example(
    meta={"id": "b12-015", "famille": "rag-ctx-notifier-lucene", "task": "RAG_FAITHFULNESS",
          "domaine": "rag", "tache": "synthese", "cas": "limite", "verbeux": True, "langage": "java"},
    task="RAG_FAITHFULNESS",
    contexte=CTX_LUCENE_NOTIFIER,
    requete="How does AskFromCodeAction notify the chat UI via NewUserMessageNotifier?",
    reponse='''
## Ce que le contexte permet d'établir

Le contexte décrit le **destinataire** du mécanisme, pas son émetteur.

`NewUserMessageNotifier` est une interface qui déclare un champ `TOPIC`, construit par `Topic.create("New user message", NewUserMessageNotifier.class)`, et une méthode `newUserMessage(String message)`. Il s'agit donc du mécanisme de bus de messages d'IntelliJ : un composant publie sur le sujet, les abonnés reçoivent l'appel.

Le contexte contient également `MessagesPanel#addUserMessage`, ce qui suggère l'existence d'un abonné côté interface, sans que le lien soit explicite.

## Ce que le contexte ne permet pas d'établir

`AskFromCodeAction` **n'apparaît dans aucun extrait**. Je ne peux donc pas dire :

- à quel moment cette action publie sur le sujet ;
- quel contenu elle transmet dans le message ;
- ni même confirmer qu'elle utilise bien ce mécanisme plutôt qu'un autre.

## Conclusion

Répondre à la question posée exigerait le code de `AskFromCodeAction`, absent du contexte fourni. Je peux décrire le canal de notification, pas son utilisation par cette action.
''',
    checks={"affirmations_etayees": True, "absence_invention": True, "citations_exactes": True},
    thinking='''
1. Énumération des éléments clés : le contexte fournit l'interface `NewUserMessageNotifier` avec son champ `TOPIC` — dont la construction `Topic.create("New user message", NewUserMessageNotifier.class)` est citée textuellement — et sa méthode `newUserMessage(String message)`, ainsi que `PluginNotifier` et `MessagesPanel#addUserMessage`.
2. Vérification point par point : chaque affirmation de la première partie est étayée, et la citation du champ `TOPIC` est exacte, littérale. La lecture du bus de messages est une déduction raisonnable à partir du type `Topic`, et elle est présentée comme telle. L'hypothèse d'un abonné côté interface est explicitement donnée pour une suggestion, non pour un fait. La seconde partie énonce correctement l'absence de `AskFromCodeAction`, ce qui est vérifiable dans les extraits, et refuse de combler le manque. C'est exactement la posture attendue en monde fermé : la sortie s'abstient plutôt que de produire une réponse plausible. Deux réserves de forme seulement : la réponse est longue pour ce qu'elle établit, et elle ne répond pas à la question posée — mais parce que le contexte ne le permet pas, ce qui n'est pas imputable à la sortie.
3. Synthèse : la sortie n'apporte pas la réponse attendue, mais tout ce qu'elle avance est étayé, elle n'invente rien et délimite explicitement ce que le contexte ne couvre pas. PASS.
''',
    reason="Tout ce qui est avancé vient des extraits, et l'absence d'AskFromCodeAction est explicitement constatée plutôt que comblée.",
))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"{len(EXAMPLES)} examples -> {out}")
