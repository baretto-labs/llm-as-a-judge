# Plan de composition du corpus (200 exemples)

But : éviter la dérive et les répétitions entre lots. Chaque lot pioche dans les familles listées ici et coche
sa ligne. Les quotas viennent de `PROTOCOLE.md` §2.2, les règles d'étiquetage de §1.

## Quotas cibles

| Axe | Cible | Détail |
|---|---|---|
| **Tâche** | 150 `CODE_ANALYSIS` / 25 `RAG_CONTEXT_RELEVANCE` / 25 `RAG_FAITHFULNESS` | 75 % / 12,5 % / 12,5 % — RAG cumulé 25 % |
| Domaine | 90 code / 60 théorie / 50 rag | le 60/40 code-théorie s'applique aux 150 `CODE_ANALYSIS` |
| Cas | 80 parfait / 80 défaillant / 40 limite | 40 / 40 / 20 |
| Verdict | ~100 PASS / ~100 FAIL | les 40 limites se répartissent ~20/20 |
| Verbeux + bug caché | ≥ 25 | tous FAIL, base du test de biais de verbosité |
| Verbeux + correct | **13** | contrôle inverse, tous PASS — cible ramenée de 15 le 2026-09-15, voir `../AUDIT.md` |
| Tâches (code) | 45 génération / 35 refactoring / 40 débogage | |
| Tâches (théorie) | 50 explication / 30 question_reponse | |
| Langages | ~70 java, ~60 python, ~35 typescript, ~20 sql, ~15 autres | ajusté aux outils vérifiables |

## Découpage en lots

| Lot | Exemples | ids | État |
|---|---|---|---|
| batch_01 | 5 | b01-001 → b01-005 | ✅ fait |
| batch_02 | 15 | b02-001 → b02-015 | ✅ fait (Java/Python/SQL, 31 assertions vérifiées) |
| batch_03 | 15 | b03-001 → b03-015 | ✅ fait (TS/Go/Java/Python/SQL, sondes + 16 assertions) |
| batch_04 | 15 | b04-001 → b04-015 | ✅ fait (Java/Python/TS, sondes probe04.*) |
| batch_05 | 15 | b05-001 → b05-015 | ✅ fait (Java/Python/SQL, sondes probe05.* + Probe05b) |
| batch_06 | 15 | b06-001 → b06-015 | ✅ fait (Java/Python/TS, sondes probe06.*) |
| batch_07 | 15 | b07-001 → b07-015 | ✅ fait (Java/Python/JS, sondes probe07.*) |
| batch_08 | 15 | b08-001 → b08-015 | ✅ fait (Python/Java/JS, sondes probe08.*) |
| batch_09 | 15 | b09-001 → b09-015 | ✅ fait (Python/Java/JS, sondes probe09.*) |
| batch_10 | 15 | b10-001 → b10-015 | ✅ fait (Java/Python/SQL/TS, sondes probe10.*) |
| batch_11 | 10 | b11-001 → b11-010 | ✅ fait — **les 150 `CODE_ANALYSIS` sont clos** |
| batch_12 | 15 | b12-001 → b12-015 | ✅ fait — contextes RAG réels, Lucene et Neo4j mêlés |
| batch_13 | 15 | b13-001 → b13-015 | ✅ fait — contextes RAG réels |
| batch_14 | 20 | b14-001 → b14-020 | ✅ fait — clôture du corpus à 200 |

Avancement : **200 / 200, corpus clos le 2026-09-14**, 0 erreur de validation. Les 150 `CODE_ANALYSIS` se
répartissent exactement en 90 `code` et 60 `theorie` ; les 50 exemples RAG en 25 par passe.

Les contextes réellement récupérés qui servent de matière sont versionnés dans
`verification/contexts/` : ce sont eux qui rendent les étiquettes vérifiables par un tiers.

État mesuré sur les 200 exemples : 80 `parfait` / 80 `defaillant` / 40 `limite`, soit 40 / 40 / 20 % au
point près ; 105 PASS pour 95 FAIL ; 25 cas verbeux à défaut caché (12,5 %, le protocole en exige 10 %)
et **13** verbeux corrects en contrôle, effectif désormais retenu comme cible.

⚠️ Ces compteurs décrivent la **composition**, pas ce que le corpus enseigne. L'audit du 2026-09-15
(`../AUDIT.md`) montre que toutes ces cibles pouvaient être atteintes tout en apprenant au juge un raccourci
de surface : la longueur du contenu évalué prédit le verdict à 75 % sur `CODE_ANALYSIS` et 84 % sur
`RAG_FAITHFULNESS`. Une reprise ciblée est en cours ; ne pas lancer d'entraînement avant sa fin.

Le compte de 13 verbeux corrects vient de cet audit : `b13-007` et `b14-008` étaient étiquetés `verbeux`
alors que leur sortie évaluée est le placeholder constant de 126 caractères — la verbosité était dans le
contexte, pas dans la sortie. Le compte annoncé de 15 était donc faux depuis l'origine, et non dégradé par
la correction.

La compensation sur les cas a été répartie au fil des lots RAG, le solde tombant sur le dernier lot ; le
détail du calcul est conservé dans la table « Composition imposée du batch_14 » plus bas.

⚠️ Polarité des contrôles supplémentaires. Un contrôle qui n'apparaîtrait qu'avec une seule valeur
apprendrait au juge un raccourci par nom, au lieu de lui faire lire la description du critère.

✅ **Équilibrage terminé au 2026-09-13** : les 9 contrôles supplémentaires (`aucune_dependance_externe`,
`contrainte_disponibilite`, `dependance_autorisee`, `durabilite_garantie`, `format_impose`,
`perimetre_respecte`, `signature_conforme`, `signature_publique_inchangee`, `validation_entree`) apparaissent
chacun avec les deux polarités. À maintenir pour tout nouveau contrôle introduit, y compris dans les lots RAG :
un contrôle à polarité unique enseigne un raccourci par nom.

Les lots suivants peuvent être produits par des modèles tiers : voir `../PROMPT_GENERATION.md`.
Règle retenue — la matière à juger peut venir d'ailleurs, l'étiquetage reste fait par un annotateur
unique et toute affirmation chiffrée doit être vérifiée par exécution avant intégration.

Familles consommées par batch_02 : injection SQL, `equals`/`hashCode` (code et théorie), try-with-resources,
argument par défaut mutable, `COUNT(*)` sur LEFT JOIN, durée compacte, signature imposée, niveaux d'isolation,
GIL, JWT signé vs chiffré, index B-tree vs hash, checked vs unchecked.

Familles consommées par batch_03 : `chunk` générique TS, `forEach` async, pool de workers Go, aliasing de slice Go,
`Optional.orElse` évalué systématiquement, contrainte « pas de regex », compréhension de dictionnaire, sargabilité
des dates, typage structurel TS, `ETag` vs `Cache-Control`, merge vs rebase, `record` vs classe immuable,
asyncio et multi-cœurs, hachage de mots de passe.

Familles consommées par batch_04 : `ConcurrentModificationException` intermittente, `Arrays.asList` de taille fixe,
flux réutilisé, monnaie en `double`, concaténation en boucle, `timedelta` et changement d'heure, copie superficielle,
retour arrière catastrophique, perte de `this`, tri par défaut JS, entiers 64 bits en JSON, `==` vs `===`,
pile et tas, idempotence REST, verrous optimistes et pessimistes.

Familles consommées par batch_11 : validation d'URL de rappel (paire contrastive), jointure de chemin avec
segment absolu, `NOT IN` et `NULL`, `LocalDateTime` et changement d'heure, `encodeURI` contre
`encodeURIComponent`, logique à trois valeurs, conversion numérique, casse et normalisation Unicode,
durée physique contre écart d'horloge.

Familles consommées par batch_10 : contrat de comparateur, comparateur par soustraction, `TreeSet` et
`compareTo` incohérent, `__eq__` sans `__hash__`, configuration gelée, écriture durable, ordre des colonnes
d'un index composite, `LIKE` et index, `any` contre `unknown` (code et théorie), tri par clé composite,
`finalize` et `Cleaner`, index couvrant, migration par expansion-contraction, `Strict-Transport-Security`.

Familles consommées par batch_09 : appel de commande externe (paire contrastive), appartenance à un
ensemble, bornes de tranche, valeur nulle dans une map, rétention d'annotation, fermeture dans une boucle,
égalité de dates, signature publique figée, `SameSite` et CSRF, liste blanche contre liste noire, pool de
connexions, journalisation de données clients, capture d'exception trop large, bascule DNS.

Familles consommées par batch_08 : persistance par `pickle` (paire contrastive), imports circulaires,
dépendance externe interdite, clé mutable dans une table de hachage, `serialVersionUID`, pollution de
prototype, égalité de `NaN`, tri d'objets sans comparateur, mesure et préchauffage JIT, chargement de
classes, saga et transactions distribuées, HTTP/2 contre HTTP/3, `is` contre `==`, mémoïsation.

Familles consommées par batch_07 : verrous croisés (paire contrastive), initialisation paresseuse non
synchronisée, types bruts et effacement, générateur épuisé, décorateur sans `functools.wraps`, transaction
sqlite3 non validée, XSS par `innerHTML`, ordre micro/macro-tâches, double-checked locking, TLS et paramètres
d'URL, limitation de débit, gestionnaires de contexte, tempête de réessais.

Familles consommées par batch_06 : exceptions avalées par `CompletableFuture` (paire contrastive), paresse des flux,
`ThreadLocal` en pool, comparaison de secret non constante, attribut de classe mutable, lecture de fichier volumineux,
analyse des chaînes de date en JS, clonage profond, `System.gc()`, cycles et ramasse-miettes Python, CORS,
WebSocket vs SSE, `var` et inférence, migration sans interruption.

Familles consommées par batch_05 : `HashMap` partagée entre threads, dépassement d'entier en recherche binaire,
tri stable en deux passes, encodage par défaut de `open()`, comparaison de versions, requêtes N+1, pagination par
`OFFSET`, `__slots__`, modulo négatif, pool de chaînes et `intern`, théorème CAP, versionnage sémantique,
TCP vs UDP, codes 401 et 403, périmètre de dénormalisation.

Chaque lot respecte localement la ventilation (≈ 9 code / 6 théorie, ≈ 6 parfait / 6 défaillant / 3 limite) pour
qu'un arrêt en cours de route laisse un corpus équilibré.

## Matière RAG : l'extraction réelle

Le corpus est clos. Les 50 contextes RAG proviennent tous d'extractions réelles ; la procédure et les
pièges rencontrés sont consignés ici, et resteront valables pour toute extension ultérieure du corpus.

⚠️ Les contextes RAG doivent provenir de **récupérations réelles** via `QuestionCorpus` et les stratégies
Lucene / Neo4j du dépôt. Un contexte inventé serait trop propre : ni bruit, ni doublons, ni troncature au
milieu d'une méthode — donc un juge inutilisable sur les sorties réelles du moteur.

### Procédure d'extraction, et les pièges rencontrés le 2026-09-14

Harnais : `verification/ExtractRagContexts.java`, lancé avec le classpath Maven du projet.

```bash
mvn -q compile test-compile
mvn -q dependency:build-classpath -Dmdep.outputFile=cp.txt -Dmdep.includeScope=test
java -cp "target/classes:target/test-classes:$(cat cp.txt)" ExtractRagContexts.java \
     ~/Workspaces/Labs/OllamAssist/src/main/java sortie.jsonl lucene hybrid
```

**Indexer `src/main/java`, jamais la racine du dépôt.** La racine d'OllamAssist contient une copie de
`llm-as-a-judge` sous `tmp/`, donc `QuestionCorpus.java` lui-même, ainsi qu'un fichier
`benchmark-results/2026-05-15_chunking.jsonl` reprenant les chaînes d'indices. Indexée en entier, la
codebase fait remonter le corpus de questions dans le contexte : les 30 questions affichaient alors **100 %
de couverture d'indices**, artefact pur. Le périmètre propre compte 162 fichiers contre 277 pour la racine,
dont 83 sous `src/test`.

**Ne jamais labelliser `contexte_suffisant` d'après `couverture_indices`.** Cette métrique ne mesure qu'une
présence de sous-chaîne ; il faut lire les extraits.

Trois pièges du harnais, tous corrigés mais à connaître :

| Piège | Symptôme | Correctif |
|---|---|---|
| Presets en kebab-case | `IllegalArgumentException: Preset inconnu: 'hybridGraph'` | `knn-only`, `hybrid`, `hybrid-graph`, `hybrid-graph-hyde`, `full` |
| `String.format` sans locale | JSON invalide, `"couverture_indices":1,000` | `Locale.ROOT` imposé |
| Exécution via `\| grep \| tail` | code de sortie 0 malgré une exception | lire le journal, pas seulement le code |

**Volume à traiter.** Lucene renvoie 10 extraits par question, médiane 665 caractères, contexte complet de
2 823 à 33 124 caractères sur le périmètre propre — bien trop pour des exemples à `--max-seq-length 2048`.
Chaque exemple RAG retiendra donc un **sous-ensemble d'extraits** (2 à 4), choisi pour illustrer le cas visé,
en conservant les extraits tels quels sans les réécrire.

### Récupération mesurée sur le périmètre propre (Lucene, preset `hybrid`)

Une fois la contamination écartée, la couverture d'indices varie enfin : 22 questions à 100 %, et 8 en
dessous. Ces 8 fournissent les cas `RAG_CONTEXT_RELEVANCE` en échec **sans avoir à dégrader le moteur**.

| Couverture | Question | Indices absents |
|---|---|---|
| 0 % | `calculateDynamicThreshold` dans `LuceneEmbeddingStore` | les trois |
| 33 % | interfaces implémentées par `OllamaService` | `Disposable`, `ModelListener` |
| 33 % | `OllamAssistStartup` initialise `EditorListener` | `OllamAssistStartup`, `execute` |
| 33 % | `SelectionGutterIcon` déclenche `OverlayPromptPanelFactory` | les deux classes |
| 50 % | méthodes de l'interface `Assistant` | `refactor`, `TokenStream` |
| 50 % | `AskFromCodeAction` notifie via `NewUserMessageNotifier` | `AskFromCodeAction` |
| 67 % | en-tête d'authentification d'`AuthenticationHelper` | `createBasicAuthHeader` |
| 75 % | ce qu'implémente `LuceneEmbeddingStore` | `Closeable` |

⚠️ Le cas à 67 % est particulier et utile : `createBasicAuthHeader` **n'existe pas** dans OllamAssist, la
méthode réelle étant `buildAuthorizationHeaderValue(AuthMode, String, String, String)`. L'indice attendu du
corpus est donc lui-même erroné. C'est la matière idéale d'un exemple `RAG_FAITHFULNESS` : une réponse qui
cite `createBasicAuthHeader` doit être rejetée comme non étayée, alors même qu'elle paraît plausible. Mieux
encore, l'extrait retenu contient la Javadoc du fichier, qui impose explicitement de passer par
`createAuthorizationHeaderValue()` ou `authHeaders()` : le contexte **contredit** la réponse plausible.

### Neo4j sur le même périmètre (preset `hybrid-graph`)

Indexation des 162 fichiers en 28,8 s. Les deux sources sont complémentaires, et le graphe présente un
avantage pratique décisif :

| | Lucene `hybrid` | Neo4j `hybrid-graph` |
|---|---|---|
| Extraits par question | 10 | 5 |
| Taille médiane d'un extrait | 665 car. | 287 car. |
| Contexte complet | 2 823 – 33 124 car. | 837 – 2 886 car. |
| Questions sous 100 % de couverture | 8 | **16** |
| Forme des extraits | blocs de code | nœuds `=== fqn.methode(args) [Function] ===` |

Le contexte Neo4j **tient directement** dans un exemple à `--max-seq-length 2048`, sans sélection d'extraits,
et offre deux fois plus de cas de récupération partielle. Les deux formats seront représentés dans le corpus :
un juge qui n'a vu qu'une mise en forme apprendrait à la reconnaître au lieu de lire la rubrique.

### Découpage des lots RAG

| Lot | Exemples | Contenu |
|---|---|---|
| batch_12 | 15 | ✅ fait — 8 `RAG_CONTEXT_RELEVANCE`, 7 `RAG_FAITHFULNESS`, sources Lucene et Neo4j mêlées |
| batch_13 | 15 | ✅ fait — 7 `RAG_CONTEXT_RELEVANCE`, 8 `RAG_FAITHFULNESS` |
| batch_14 | 20 | ✅ fait — 10 `RAG_CONTEXT_RELEVANCE`, 10 `RAG_FAITHFULNESS`, clôture du corpus à 200 |

**Composition imposée du batch_14, seule combinaison qui atteigne les cibles — produite telle quelle,
les compteurs finaux tombent au point près :**

| Axe | Fait sur 180 | À produire sur 20 |
|---|---|---|
| `RAG_CONTEXT_RELEVANCE` | 15 | **10** |
| `RAG_FAITHFULNESS` | 15 | **10** |
| `parfait` | 71 | **9** |
| `defaillant` | 73 | **7** |
| `limite` | 36 | **4** |
| verbeux à défaut caché | 24 | **1** |
| verbeux correct | 14 | **1** |

**Contextes consommés par les trois lots RAG**, à ne pas réutiliser tels quels si le corpus est un jour
étendu. Un même symbole extrait par les deux moteurs compte pour deux contextes distincts : les formes
diffèrent (blocs de code contre nœuds de graphe), et le corpus les représente exprès toutes les deux.

| Lot | Lucene `hybrid` | Neo4j `hybrid-graph` |
|---|---|---|
| batch_12 | `calculateDynamicThreshold`, `AuthenticationHelper`, `OllamaService`, `NewUserMessageNotifier` | `AuthenticationHelper`, `OllamaService`, `ContextRetriever.retrieve` |
| batch_13 | `SuggestionCache`, `PrerequisiteService`, `LuceneEmbeddingStore implements` | `DocumentIndexingPipeline` (réessais), `BracketCallParser`, `Assistant`, `DocumentIngestFactory` |
| batch_14 | `DocumentIndexingPipeline.processBatch` (corps), `ContextRetriever` (sources) | `EnhancedCompletionService`, `RefactorAction.dismiss`, implémentations de `ToolCallParser`, `FileCreator` / `FileApprovalNotifier` |

### Familles RAG — passe A, `RAG_CONTEXT_RELEVANCE`

récupération exacte sur question LOCAL · extraits du bon fichier mais mauvaise méthode · contexte suffisant
noyé sous dix extraits hors sujet · question CROSS_MODULE avec un seul des deux modules récupéré ·
extraits tronqués au milieu de la signature · doublons du même chunk occupant la fenêtre · récupération
d'une classe homonyme dans un autre package · contexte vide ou uniquement des imports

### Familles RAG — passe B, `RAG_FAITHFULNESS`

réponse entièrement étayée · **affirmation vraie dans l'absolu mais absente du contexte** (cas décisif de la
posture monde fermé) · signature de méthode inventée · nom de classe correct mais paramètres hallucinés ·
comportement extrapolé d'un nom de méthode sans lire le corps · citation déformée d'un extrait ·
réponse qui admet correctement ne pas savoir · mélange d'un extrait fourni et d'une connaissance externe

## Familles de scénarios

Une famille = une consigne, déclinée en 1 à 3 réponses (souvent une paire contrastive PASS/FAIL). Les variantes d'une
même famille restent du même côté du split, `dataset_tools.py` s'en charge via le champ `famille`.

### Code — sécurité (≈ 20 exemples)
injection SQL par concaténation · traversée de répertoire ✅(b01-002) · secret en dur dans le code · désérialisation
non fiable · XSS par innerHTML · CSRF absent sur mutation · comparaison de mots de passe non constante · hachage
MD5/SHA1 pour mot de passe · JWT sans vérification de signature · upload sans validation de type · redirection ouverte
· SSRF sur URL utilisateur

### Code — concurrence (≈ 15)
`count++` sur volatile ✅(b01-005, théorie) · double-checked locking sans volatile · `HashMap` partagée non
synchronisée · ThreadLocal non nettoyé en pool · `synchronized` sur une mauvaise instance · async/await oublié en TS ·
`Promise.all` vs boucle séquentielle · deadlock par ordre de verrous · `CompletableFuture` sans gestion d'exception ·
GIL et threads Python

### Code — correction (≈ 30)
off-by-one sur borne · mutation de l'entrée · égalité de flottants · fuseaux horaires et dates · encodage UTF-8 ·
`null`/`None` non géré · division entière · tri instable supposé stable · `equals` sans `hashCode` · intervalles
fusionnés ✅(b01-003) · regex catastrophique · comparaison de versions · arrondi monétaire · pagination hors bornes

### Code — API et refactoring (≈ 25)
`Collectors.toMap` et doublons ✅(b01-001) · stream réutilisé · `Optional` mal employé · N+1 ORM · transaction
manquante · `try-with-resources` oublié · sémantique changée par un refactoring · extraction de méthode qui casse un
effet de bord · `Arrays.asList` immuable · mutable default argument Python · shallow vs deep copy · itération avec
suppression concurrente

### Code — performance (≈ 10)
boucle O(n²) évitable · concaténation de chaînes en boucle · requête dans une boucle · index manquant · lecture
intégrale d'un fichier volumineux · cache absent sur appel coûteux

### Code — génération sur consignes strictes (≈ 20, source des cas limites)
signature imposée · version de langage imposée · dépendance interdite · format de sortie imposé · typage strict exigé ·
consignes formulées comme facultatives (« si possible ») · limite de lignes · style de docstring demandé

### Théorie — Java / JVM (≈ 25)
`thenApply` vs `thenCompose` ✅(b01-004) · `volatile` vs `synchronized` ✅(b01-005) · `equals`/`hashCode` · GC et
générations · heap vs stack · `String.intern` · classloaders · records vs Lombok · checked vs unchecked exceptions ·
`Stream` paresseux · `var` et inférence

### Théorie — bases de données (≈ 15)
niveaux d'isolation et lectures fantômes · index B-tree vs hash · `EXPLAIN` et plans · transactions distribuées ·
CAP · normalisation vs dénormalisation · verrous pessimistes/optimistes · migrations sans interruption

### Théorie — web et réseau (≈ 15)
cache HTTP et `ETag` · CORS · JWT vs session · TLS et certificats · TCP vs UDP · idempotence REST · codes de statut ·
WebSocket vs SSE

### Théorie — Python, TS, outillage (≈ 25)
GIL et parallélisme · `asyncio` vs threads · GC par comptage de références · `__slots__` · type hints et exécution ·
`this` en JS · types structurels TS · `strictNullChecks` · arbres de rebase Git · sémantique du versionnage

## Règles de production d'un lot

1. Écrire les exemples dans un script générateur, jamais à la main dans le JSONL (échappements).
2. **Vérifier par exécution** tout ce qui peut l'être (Java, Python, TypeScript, SQL). Une affirmation du `<thinking>`
   qui n'a pas été vérifiée doit être retirée ou reformulée.
3. `make validate` doit passer à 0 erreur, puis `make stats` pour contrôler la dérive.
4. Cocher les familles utilisées dans ce fichier et mettre à jour la table des lots.
