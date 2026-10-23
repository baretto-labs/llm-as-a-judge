CONVENTIONS DE NOTATION

1. Verdict. verdict = "PASS" si et seulement si tous les contrôles de checks valent true. Aucune exception.

2. Consignes obligatoires contre préférences.
   - Consigne formulée comme préférence (« si possible », « si tu as le temps ») non suivie : contrôle à
     true, écart mentionné dans le <thinking>.
   - Sortie verbeuse mais correcte : jamais pénalisée pour sa seule longueur.
   - Exigence explicite et vérifiable non respectée (signature, version, dépendance interdite, format,
     périmètre) : contrôle à false.

3. Contrôle dédié. Toutes les consignes obligatoires de la requête sont respectées, à l'exception de
   celles couvertes par un contrôle dédié, qui les évalue séparément.

4. Portée de citations_exactes (RAG_FAITHFULNESS). citations_exactes ne sanctionne que la déformation de
   matériau réellement puisé dans le contexte. Lorsqu'une sortie invente de bout en bout sans rien citer
   ni paraphraser du contexte, il n'existe aucune citation à déformer et le contrôle vaut vrai par
   vacuité — le rejet est alors porté par affirmations_etayees et absence_invention, et le verdict reste
   FAIL puisque PASS exige tous les contrôles.

EXEMPLES DE JUGEMENTS, AVEC LE RAISONNEMENT QUI LES JUSTIFIE

Six cas limites déjà tranchés. Ils montrent comment les conventions
ci-dessus s'appliquent quand le cas n'est pas franc. Juge l'item qui
t'est soumis de la même façon ; ne recopie aucun de ces verdicts.

### EXEMPLE 1 — tâche CODE_ANALYSIS, cas limite, verdict attendu PASS

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Nous comparons des identifiants saisis par les utilisateurs en passant par une mise en minuscules. Quels pièges ? Si tu as le temps, dis un mot des identifiants réservés.

### SORTIE À ÉVALUER
## Deux problèmes distincts

La mise en minuscules traite la **casse**. Elle ne traite ni la **représentation** des caractères, ni les règles propres à certaines langues.

## La casse dépend de la langue

La mise en minuscules n'est pas une opération universelle. Le turc distingue le I avec et sans point, si bien qu'un même caractère se replie différemment selon la locale active — un comportement qui dépend alors du serveur, ce qui est la pire des dépendances pour une comparaison d'identité.

Le pliage de casse, prévu pour la comparaison plutôt que pour l'affichage, est plus adapté : en Python, `casefold` replie l'eszett allemand `ß` vers `ss`, là où une simple mise en minuscules le laisse tel quel. Deux utilisateurs saisissant l'une ou l'autre forme seraient sinon considérés comme distincts.

## La même chaîne peut s'écrire de deux façons

Un caractère accentué existe sous forme composée, un seul point de code, et sous forme décomposée, une lettre suivie d'un accent combinant. Les deux s'affichent à l'identique et ne sont pas égales : leur longueur diffère même, une contre deux pour un `é`.

La parade est la normalisation, en forme NFC le plus souvent, appliquée **avant** toute comparaison ou tout stockage.

## L'ordre des opérations

Normalisez d'abord, repliez la casse ensuite, puis comparez. L'inverse laisse passer des cas où le repli produit des séquences non normalisées.

## En pratique

Un identifiant devrait être normalisé et replié une fois, à l'entrée, puis stocké sous cette forme canonique — avec la forme originale conservée à part pour l'affichage.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées.

--- JUGEMENT ATTENDU, AVEC SON RAISONNEMENT ---

<thinking>
1. Analyse de l'explication : les deux problèmes sont correctement distingués, et chacun est exact. La dépendance de la mise en minuscules à la locale est réelle, et l'exemple turc est le cas d'école.
2. Vérification des contraintes : les affirmations chiffrables sont exactes. Le pliage de casse replie bien `ß` vers `ss` là où la mise en minuscules ne le fait pas : `'ß'.casefold() == 'ss'` est vrai alors que `'ß'.lower() == 'ss'` est faux. Le cas turc est confirmé dans les deux langages : `'ADMİN'` mis en minuscules ne vaut pas `'admin'`. Les deux formes de représentation se distinguent de même : composée et décomposée ne sont pas égales, leurs longueurs valent respectivement 1 et 2, et l'égalité est rétablie après normalisation commune. L'ordre des opérations recommandé est correct. En revanche, la demande facultative sur les identifiants réservés n'est pas traitée, alors qu'elle prolongeait naturellement le propos. La réponse est par ailleurs longue, avec cinq sections pour un sujet qui en appelait deux.
3. Synthèse : l'obligatoire est exact, l'omission porte sur une demande explicitement facultative, et la verbosité seule ne justifie pas un échec. PASS.
</thinking>
{
  "checks": {
    "exactitude_technique": true,
    "absence_de_bugs": true,
    "respect_consignes": true
  },
  "verdict": "PASS",
  "reason": "Casse et normalisation exactement distinguées ; seuls les identifiants réservés, facultatifs, manquent."
}

### EXEMPLE 2 — tâche CODE_ANALYSIS, cas limite, verdict attendu FAIL

### CONTEXTE / RAG
(aucun contexte fourni — évaluation en monde ouvert : mobilise tes connaissances techniques)

### ENTREE / REQUÊTE
Implémente **exactement** cette signature, en Java 17 et sans dépendance externe :

```java
public static Optional<String> firstNonBlank(List<String> values)
```

Elle renvoie la première valeur non nulle et non blanche de la liste, ou `Optional.empty()` si aucune ne convient.

### SORTIE À ÉVALUER
```java
public static String firstNonBlank(List<String> values) {
    if (values == null) return null;
    for (String value : values) {
        if (value != null && !value.isBlank()) return value;
    }
    return null;
}
```

## Choix d'implémentation

`isBlank()`, introduite en Java 11, couvre d'un seul test la chaîne vide et les chaînes composées uniquement d'espaces ou de tabulations. Inutile donc d'écrire `value.trim().isEmpty()`, qui alloue en prime une chaîne intermédiaire à chaque élément parcouru.

Le parcours s'arrête au premier élément valide : quand la valeur utile est en tête de liste, on ne paie qu'une itération. Une version à base de `Stream` — `values.stream().filter(...).findFirst()` — serait plus déclarative, mais monte un pipeline complet pour un besoin qui tient en une boucle.

Le cas de la liste `null` est traité en amont, ce qui évite la `NullPointerException` que lèverait le `for` amélioré en tentant d'obtenir un itérateur.

## Sur le type de retour

La logique est identique à ce qui était demandé, j'ai simplement préféré renvoyer `null` plutôt qu'un `Optional` : c'est plus léger et ça évite une allocation par appel. Sur un chemin appelé en boucle serrée, cette allocation finit par se voir au profilage.

### CRITÈRES DE VALIDATION
1. exactitude_technique: Le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
2. absence_de_bugs: Aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable dans la sortie.
3. respect_consignes: Toutes les consignes obligatoires de la requête sont respectées, à l'exception de celles couvertes par un contrôle dédié ci-dessous, qui les évalue séparément.
4. signature_conforme: La signature est exactement celle imposée par la requête, type de retour compris.

--- JUGEMENT ATTENDU, AVEC SON RAISONNEMENT ---

<thinking>
1. Analyse du code : la logique de sélection est correcte. `isBlank()` couvre bien la chaîne vide et les chaînes composées d'espaces, le `null` de la liste est écarté avant l'appel, et le parcours renvoie le premier élément valide. Sur une liste `[null, "  ", "", "premier", "second"]`, la valeur retournée est `"premier"`. Les justifications ajoutées sont exactes : `isBlank()` date bien de Java 11, `trim().isEmpty()` alloue bien une chaîne intermédiaire, et le `for` amélioré lèverait bien une `NullPointerException` sur une liste nulle.
2. Vérification des contraintes : la signature imposée n'est pas respectée. La consigne exigeait **exactement** `Optional<String>` comme type de retour, la réponse renvoie `String` et signale l'absence de valeur par `null`. Ce n'est pas un détail de style : tout appelant écrit contre l'API demandée ne compile pas, et la sentinelle `null` réintroduit précisément le risque que `Optional` sert à écarter. La justification par l'allocation évitée ne tient pas face à une exigence explicite.
3. Synthèse : le code est juste et sans bug, mais une consigne obligatoire et non ambiguë est ignorée, ce qui suffit à faire échouer la réponse. FAIL.
</thinking>
{
  "checks": {
    "exactitude_technique": true,
    "absence_de_bugs": true,
    "respect_consignes": true,
    "signature_conforme": false
  },
  "verdict": "FAIL",
  "reason": "La signature imposée n'est pas respectée : retour String et sentinelle null au lieu du Optional<String> exigé."
}

### EXEMPLE 3 — tâche RAG_CONTEXT_RELEVANCE, cas limite, verdict attendu PASS

### CONTEXTE / RAG
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

Method: fr.baretto.ollamassist.chat.askfromcode.OllamaGutterIconRenderer#hashCode [...]

### ENTREE / REQUÊTE
What authentication header does AuthenticationHelper generate?

### SORTIE À ÉVALUER
(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de recherche a retournés pour cette requête)

### CRITÈRES DE VALIDATION
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

--- JUGEMENT ATTENDU, AVEC SON RAISONNEMENT ---

<thinking>
1. Énumération des éléments clés : le premier extrait est le fichier `AuthenticationHelper.java` lui-même, avec sa documentation ; le deuxième est l'énumération `AuthMode` et sa documentation détaillée. Suivent deux extraits sans rapport direct, `PrerequisiteService#readAuthenticated` et `OllamaGutterIconRenderer#hashCode`.
2. Vérification point par point : la classe visée est présente, le contexte est donc pertinent. Sur la suffisance, la documentation répond à la question posée : deux schémas mutuellement exclusifs sélectionnés par `AuthMode`, Basic avec `username:password` encodé en Base64, et Bearer pour un jeton ou une clé d'API, les deux reposant sur l'unique en-tête `Authorization`. La documentation nomme en outre les points d'entrée obligatoires, `createAuthorizationHeaderValue()` et `authHeaders()`. C'est suffisant pour répondre entièrement. Deux réserves : le premier extrait est tronqué en pleine phrase, ce qui prive du détail de construction de la valeur, et le dernier extrait est franchement hors sujet. Ni l'un ni l'autre n'empêche de répondre, et l'information utile occupe les deux premiers extraits.
3. Synthèse : la troncature et un extrait parasite ne suffisent pas à disqualifier un contexte qui contient la classe visée et la description complète des deux schémas. PASS.
</thinking>
{
  "checks": {
    "contexte_pertinent": true,
    "contexte_suffisant": true,
    "bruit_maitrise": true
  },
  "verdict": "PASS",
  "reason": "Le fichier AuthenticationHelper et l'énumération AuthMode répondent entièrement à la requête, malgré une troncature et un extrait parasite."
}

### EXEMPLE 4 — tâche RAG_CONTEXT_RELEVANCE, cas limite, verdict attendu FAIL

### CONTEXTE / RAG
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
  fr.baretto.ollamassist.chat.service.OllamaService -[IMPLEMENTS]-> Disposable

### ENTREE / REQUÊTE
How does DocumentIngestFactory create the embedding model with DJL fallback to Ollama?

### SORTIE À ÉVALUER
(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur de recherche a retournés pour cette requête)

### CRITÈRES DE VALIDATION
1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet.

--- JUGEMENT ATTENDU, AVEC SON RAISONNEMENT ---

<thinking>
1. Énumération des éléments clés : la requête porte sur `createEmbeddingModel` et sur le repli de DJL vers Ollama. Le contexte donne le nœud de classe `DocumentIngestFactory`, avec le champ `FALLBACK_EMBEDDING_MODEL`, puis la fonction `create(EmbeddingStore<TextSegment>, Project)`, et trois extraits sur `OllamaSettings`, `DefaultJsonCodecFactory` et `OllamaService`.
2. Vérification point par point : la classe visée est présente et le champ `FALLBACK_EMBEDDING_MODEL` touche directement au sujet du repli, donc la pertinence est acquise. La suffisance ne l'est pas : la fonction demandée, `createEmbeddingModel`, ne figure pas dans le contexte — seule `create(...)`, de signature et de rôle différents, est fournie. Rien ne montre le modèle DJL, ni l'exception qui déclenche le repli, ni le modèle Ollama de remplacement. Le nom du champ **suggère** un repli sans en révéler le mécanisme ; c'est précisément le genre d'indice qui invite à extrapoler. Le bruit reste maîtrisé, les trois extraits hors sujet étant courts et clairement identifiés.
3. Synthèse : le contexte est authentiquement pertinent et nomme le repli, mais la fonction interrogée en est absente, donc il ne permet pas de répondre. FAIL.
</thinking>
{
  "checks": {
    "contexte_pertinent": true,
    "contexte_suffisant": false,
    "bruit_maitrise": true
  },
  "verdict": "FAIL",
  "reason": "Le champ FALLBACK_EMBEDDING_MODEL évoque le repli, mais createEmbeddingModel est absente : seule create(...) figure au contexte."
}

### EXEMPLE 5 — tâche RAG_FAITHFULNESS, cas limite, verdict attendu PASS

### CONTEXTE / RAG
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

Type: class fr.baretto.ollamassist.chat.rag.HybridRetriever implements ContentRetriever [...]

### ENTREE / REQUÊTE
What is the role of HybridRetriever relative to ContextRetriever?

### SORTIE À ÉVALUER
Le contexte établit peu de choses sur ce point précis.

Ce qui est visible : `HybridRetriever` et `ContextRetriever` implémentent toutes deux `ContentRetriever`. La documentation de `ContextRetriever` indique par ailleurs que sa source principale est « the main ContentRetriever, typically backed by an embedding store or an internal RAG engine ».

Ce qui ne l'est pas : aucun extrait ne montre de relation directe entre les deux classes — ni composition, ni appel, ni héritage. L'hypothèse que `HybridRetriever` tienne le rôle de ce `ContentRetriever` principal est cohérente avec les deux éléments ci-dessus, mais elle n'est pas établie par le contexte, qui ne contient aucun corps de méthode ni aucun champ de `ContextRetriever`.

### CRITÈRES DE VALIDATION
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

--- JUGEMENT ATTENDU, AVEC SON RAISONNEMENT ---

<thinking>
1. Énumération des éléments clés : le contexte donne `ContextRetriever implements ContentRetriever` avec sa documentation, et `HybridRetriever implements ContentRetriever`. Aucun extrait ne relie les deux classes.
2. Vérification point par point : les deux relations d'implémentation citées figurent explicitement, et la phrase de documentation est reprise littéralement, guillemets compris. Le point délicat est l'hypothèse formulée dans le dernier paragraphe : la sortie l'énonce, en indique la cohérence, puis dit explicitement qu'elle **n'est pas établie** par le contexte, en donnant la raison — aucun champ ni corps de `ContextRetriever` n'est fourni. Une hypothèse présentée comme telle, avec sa limite, ne constitue pas une invention ; l'aurait été une affirmation du même contenu au présent de l'indicatif. Aucune citation n'est déformée.
3. Synthèse : la réponse n'établit pas grand-chose, mais tout ce qu'elle avance est étayé, et l'hypothèse avancée est explicitement marquée comme non établie. PASS.
</thinking>
{
  "checks": {
    "affirmations_etayees": true,
    "absence_invention": true,
    "citations_exactes": true
  },
  "verdict": "PASS",
  "reason": "Les deux relations d'implémentation sont exactes, la citation est littérale, et l'hypothèse sur le rôle est explicitement donnée pour non établie."
}

### EXEMPLE 6 — tâche RAG_FAITHFULNESS, cas limite, verdict attendu FAIL

### CONTEXTE / RAG
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

Method: fr.baretto.ollamassist.chat.rag.DocumentIndexingPipeline#start [...]

### ENTREE / REQUÊTE
How does DocumentIndexingPipeline process documents in batches?

### SORTIE À ÉVALUER
D'après le corps fourni de `processBatch()` :

1. La méthode sort immédiatement si le pipeline ne tourne pas ou si la file est vide. La garde s'écrit, dans le corps fourni, `if (isRunning && processingQueue.isEmpty()) return;`.
2. Elle franchit une barrière de synchronisation avec `processingPhaser.arriveAndAwaitAdvance()`.
3. Elle prend le verrou `processingLock`.
4. Elle alloue une liste dimensionnée à `BATCH_SIZE` et y draine au plus `BATCH_SIZE` éléments de la file, via `processingQueue.drainTo(currentBatch, BATCH_SIZE)`.

La valeur de `BATCH_SIZE` n'est pas visible : la constante est utilisée, jamais déclarée dans les extraits. Le corps est par ailleurs tronqué après le test `if (!currentBatch.isEmpty`, donc le traitement effectif du lot n'est pas observable.

### CRITÈRES DE VALIDATION
1. affirmations_etayees: Chaque affirmation de la sortie est explicitement soutenue par un extrait du contexte fourni.
2. absence_invention: La sortie n'introduit aucun symbole, signature, valeur ou comportement absent du contexte, même s'il serait vrai par ailleurs.
3. citations_exactes: Les extraits cités ou paraphrasés par la sortie correspondent fidèlement au contexte fourni.

--- JUGEMENT ATTENDU, AVEC SON RAISONNEMENT ---

<thinking>
1. Énumération des éléments clés : le contexte fournit le corps de `processBatch` jusqu'à sa troncature. La garde d'entrée y figure textuellement, `if (!isRunning || processingQueue.isEmpty())` suivi d'un `return`, puis viennent le phaser, le verrou, l'allocation et le drainage.
2. Vérification point par point : le fond est solide. Les quatre étapes énumérées correspondent ligne à ligne au corps fourni, la formulation « au plus `BATCH_SIZE` éléments » est fidèle à la sémantique de `drainTo` sans rien ajouter, et les deux réserves finales sont justes : la constante est effectivement utilisée sans être déclarée, et la troncature est signalée au point exact où elle survient. Aucune valeur n'est avancée, aucune méthode absente n'est invoquée — rien n'est inventé et l'ensemble de la description est soutenu par les extraits. Mais la citation de la garde est **déformée**. La sortie l'annonce comme tirée du corps fourni et la rend `if (isRunning && processingQueue.isEmpty()) return;` : la négation a disparu et le `||` est devenu `&&`. La condition ainsi écrite ne sortirait que sur un pipeline actif **et** une file vide, soit l'inverse partiel de la garde réelle. La phrase en prose qui la précède reste correcte, ce qui rend l'écart d'autant plus discret : seul le fragment présenté entre accents graves est faux.
3. Synthèse : rien n'est inventé et la description d'ensemble est étayée, mais un extrait donné pour littéral est restitué avec une logique altérée. En monde fermé, une citation déformée ne peut pas passer, quelle que soit la qualité du reste. FAIL.
</thinking>
{
  "checks": {
    "affirmations_etayees": true,
    "absence_invention": true,
    "citations_exactes": false
  },
  "verdict": "FAIL",
  "reason": "La garde citée comme littérale est rendue `if (isRunning && ...)` au lieu de `if (!isRunning || ...)`, alors que tout le reste de la description est étayé."
}
