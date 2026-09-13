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
| Verbeux + correct | ≥ 15 | contrôle inverse, tous PASS |
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
| batch_09 → batch_11 | 15, 15, 10 | bNN-001 → bNN-0NN | à produire — clôture des 150 `CODE_ANALYSIS` |

Avancement : **110 / 200** (dont 110 `CODE_ANALYSIS` sur 150). Reste 40 exemples de code — 24 `code`,
16 `theorie` — puis les 50 RAG.

⚠️ Polarité des contrôles supplémentaires. Un contrôle qui n'apparaîtrait qu'avec une seule valeur
apprendrait au juge un raccourci par nom, au lieu de lui faire lire la description du critère. État au
2026-09-13, après le lot 08 :

| Contrôle | Polarités observées | À produire dans les lots 09 à 11 |
|---|---|---|
| `aucune_dependance_externe` | les deux | — |
| `format_impose` | les deux | — |
| `signature_conforme` | les deux | — |
| `contrainte_disponibilite` | toujours faux | un cas **vrai** |
| `dependance_autorisee` | toujours faux | un cas **vrai** |
| `durabilite_garantie` | toujours faux | un cas **vrai** |
| `perimetre_respecte` | toujours faux | un cas **vrai** |
| `signature_publique_inchangee` | toujours vrai | un cas **faux** |
| `validation_entree` | toujours vrai | un cas **faux** |. Distribution exactement sur les cibles (60/40 domaine, 40/40/20 cas,
12 cas verbeux à bug caché soit 15,0 %, 6 cas verbeux corrects en contrôle).
Croisement cas × verdict : parfait 32 PASS, défaillant 32 FAIL, limite 11 PASS / 5 FAIL.

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

## Reste à produire après le lot 06

80 exemples faits, tous `CODE_ANALYSIS`. Il reste **70 `CODE_ANALYSIS`** (42 code / 28 théorie) et
**50 exemples RAG**, à répartir en 25 par passe.

⚠️ Les contextes RAG doivent provenir de **récupérations réelles** via `QuestionCorpus` et les stratégies
Lucene / Neo4j du dépôt. Un contexte inventé serait trop propre : ni bruit, ni doublons, ni troncature au
milieu d'une méthode — donc un juge inutilisable sur les sorties réelles du moteur.

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
