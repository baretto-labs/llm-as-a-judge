# Relecture du golden set — journal

But : les étiquettes du corpus sont produites par un modèle. Sans relecture humaine, le κ du benchmark
mesure l'accord avec ce modèle, pas avec un humain. Ce journal trace chaque exemple relu, pour que le κ
soit calculable à la fin et qu'aucun exemple ne soit oublié entre deux sessions.

Golden set : 50 exemples, tirés en `SPLIT_SEED=11`, listés dans `data/golden/test.jsonl` (non versionné,
reproductible par `make split`).

⚠️ **Le golden set a été retiré le 2026-09-15**, après le regroupement des familles RAG par contexte
d'extraction (chantier 7 de l'audit). Ce regroupement a supprimé la fuite — 0 item RAG sur 12 avec un
contexte déjà vu en entraînement, contre 9 sur 11 auparavant — mais il a changé la structure du tirage,
rendant la graine 3 caduque. Composition actuelle : 38 `CODE_ANALYSIS`, 6 `RAG_CONTEXT_RELEVANCE`,
6 `RAG_FAITHFULNESS`, cas 19/21/10, 24 PASS / 26 FAIL.

Conséquence pour la relecture : `b03-007`, relu en session 1, **est sorti du golden set**. Son arbitrage
reste acquis — il a produit la correction de périmètre de `respect_consignes`, appliquée aux 28 exemples
portant un contrôle dédié — mais il ne comptera pas dans le κ du golden. `b04-015`, `b07-011` et
`b10-015` y figurent toujours.

## Protocole

1. L'exemple est présenté **sans son étiquette** : contexte, requête, sortie à évaluer, critères. Ni
   verdict, ni `<thinking>`, ni motif. Montrer l'étiquette d'abord ancrerait l'annotateur, qui validerait
   les erreurs au lieu de les trouver.
2. L'annotateur tranche **chaque contrôle**. Le verdict en découle : PASS si et seulement si tous les
   contrôles sont vrais.
3. L'étiquette est révélée, les écarts sont arbitrés.
4. Toute correction passe par `generators/gen_batch_NN.py` puis `make regen` — **jamais** par le JSONL.
   Si un `verdict` ou un `cas` change, les strates du tirage bougent : rejouer `make split`.

## Ordre de passage

Du plus sujet à erreur au plus simple, pour que l'effort porte là où il compte.

| Session | Contenu | Pourquoi en premier |
|---|---|---|
| 1 | `b04-015`, `b07-011`, `b09-009`, `b10-015` | cas `limite` à 4 contrôles où **un seul contrôle** sépare PASS de FAIL |
| 2 | `b03-012`, `b05-008`, `b06-013`, `b07-015`, `b12-008`, `b13-013` | les 6 autres `limite` : arbitrages, donc divergence maximale entre annotateurs |
| 3-4 | les 10 items RAG restants | portent la posture monde fermé, cœur du fine-tuning |
| 5+ | les 30 `CODE_ANALYSIS` francs | validation rapide |

Plan révisé après le retirage du 2026-09-15. `b09-009` remplace `b03-007` en session 1, même profil : un
`limite` à quatre contrôles dont un seul est faux, donc à une voix de basculer. Les deux `limite` de
session 2 qui sont des items RAG — `b12-008` et `b13-013` — comptent aussi dans les 12 items RAG, d'où
les 10 restants en sessions 3-4.

## Journal

| # | id | Verdict annotateur | Verdict étiquette | Accord verdict | Écart sur les contrôles | Arbitrage |
|---|---|---|---|---|---|---|
| 1 | `b03-007` | FAIL | FAIL | ✅ | `respect_consignes` : annotateur `false`, étiquette `true` | Description corrigée, étiquette inchangée |
| 2 | `b04-015` | FAIL | FAIL | ✅ | `respect_consignes` : annotateur `false`, étiquette `true` | Description corrigée, étiquette inchangée |

**Accord verdict : 2 / 2.** Dont un seul, `b04-015`, encore dans le golden set après le retirage ;
`b03-007` en est sorti et ne comptera pas dans le κ, sans que son arbitrage soit perdu pour autant.

`b07-011` et `b10-015` ont été présentés à l'annotateur, réponse en attente. Tous deux figurent toujours
dans le golden set et n'ont pas été réécrits par la reprise : leurs verdicts restent donc valables.

## Décisions issues de la relecture

### 2026-09-15 — périmètre de `respect_consignes` (exemples 1 et 2)

L'annotateur marquait `respect_consignes` **et** le contrôle dédié à `false` ; l'étiquette ne marquait que
le contrôle dédié. Vérification sur les 200 exemples : la convention était appliquée **15 fois sur 15**,
donc systématique — mais nulle part écrite, et contredisant la description montrée au juge (« Toutes les
consignes obligatoires de la requête sont respectées »). La lecture de l'annotateur était la lecture
littérale, et elle était juste.

Arbitrage retenu : **corriger la description**, pas les étiquettes. Quand un contrôle dédié est présent,
`respect_consignes` annonce désormais qu'elle exclut ce que ce contrôle couvre. Le contrôle dédié garde
ainsi sa valeur de diagnostic — le benchmark peut dire *quelle* contrainte le juge rate, ce qui
disparaîtrait si les deux contrôles basculaient toujours ensemble.

Mis en œuvre dans `generators/gen_batch_01.py` (`RESPECT_CONSIGNES_PERIMETRE_REDUIT`), appliqué aux 28
exemples portant un contrôle dédié. Aucun `verdict` ni `cas` modifié, donc le tirage est inchangé.

## Séance du 2026-09-15 — reprise après le retirage

### 3. `b09-009` — accord sur le verdict, désaccord croisé sur deux contrôles

| | 1 `exactitude` | 2 `absence_de_bugs` | 3 `respect_consignes` | 4 `signature_publique_inchangee` |
|---|---|---|---|---|
| annotateur | **F** | V | V | **V** |
| étiquette | **V** | V | V | **F** |

Verdict **FAIL des deux côtés**. Les deux écarts vont en sens opposés, chacun voyant un défaut là où
l'autre n'en voit pas.

**Contrôle 4 — tranché, l'étiquette est maintenue.** L'annotateur a confirmé une inversion de frappe. La
signature passe bien de `total(List<Integer>)` à `total(Optional<List<Integer>>)`, ce qui rompt la
compatibilité **source** — tout appel existant cesse de compiler — et la compatibilité **binaire**, le
descripteur inscrit dans le bytecode des appelants changeant, d'où un `NoSuchMethodError` pour les jars
tiers déjà compilés. La requête posait la contrainte en toutes lettres.

**Contrôle 1 — correction proposée, EN ATTENTE DE CONFIRMATION.**

La réponse affirme : « l'appelant voit immédiatement que la valeur peut manquer, et le compilateur
l'oblige à en tenir compte ». C'est faux. Un `Optional` en **paramètre** ne contraint l'appelant à rien :
`total(null)` compile sans avertissement et lève une `NullPointerException` dans `orElseGet`. Sous le
critère « chaque affirmation technique de la sortie est vraie », `exactitude_technique` doit donc valoir
**faux**.

Le `<thinking>` actuel relève bien qu'`Optional` en paramètre contrevient à l'usage recommandé, mais le
traite comme une question de style rattachée au contrôle 4, sans jamais peser cette phrase comme une
**affirmation factuelle**. C'est un défaut d'étiquetage réel, repéré par la relecture.

Correction envisagée : `[F, V, V, F]`. Verdict inchangé (FAIL), `cas` inchangé (`limite` — le code devient
effectivement tolérant au nul, c'est l'explication qui ment), donc strate du tirage inchangée et golden set
intact. Coût nul.

**Pourquoi elle n'est pas appliquée :** l'accord a été donné en clôture de séance, l'annotateur signalant
lui-même sa fatigue. Modifier une étiquette du golden sur cette base reproduirait le raccourci — agir sur
une lecture plausible plutôt que sur une vérification — que l'audit du jour a précisément fait corriger.
À confirmer à tête reposée.

### État de la relecture

- **Accord sur le verdict : 3 / 3** (`b03-007`, `b04-015`, `b09-009`), dont 2 encore dans le golden set.
- **En attente :** `b07-011` et `b10-015`, présentés avant la pause, non réécrits depuis, toujours dans le
  golden — les réponses restent valables.
- **Reprise :** confirmer le contrôle 1 de `b09-009`, puis les deux exemples en attente, puis la session 2
  (`b03-012`, `b05-008`, `b06-013`, `b07-015`, `b12-008`, `b13-013`).

### 4. `b07-011` — premier désaccord sur un verdict, et ce qu'il révèle

| | 1 `exactitude` | 2 `absence_de_bugs` | 3 `respect_consignes` | 4 `format_impose` | verdict |
|---|---|---|---|---|---|
| annotateur, **premier passage** | — | — | — | — | **PASS** |
| étiquette | V | V | V | **F** | **FAIL** |
| annotateur, après révélation | V | V | V | F | FAIL |

**Étiquette maintenue, aucune correction du corpus.** Le contenu technique est exact de bout en bout —
condition `volatile`, décomposition de `new Holder()`, publication d'une référence partiellement
construite, JSR-133 depuis Java 5, idiome de la classe interne. Le seul contrôle fautif est le 4 : la
requête impose « trois points maximum », la réponse en aligne cinq.

**Ce que le cas révèle.** L'annotateur a évalué le fond, jugé — à raison — que tout y était exact, et
conclu PASS sans peser la contrainte de forme. Il l'a reconnu de lui-même : « je me suis concentré sur le
fond et je n'ai pas vu les 3 points ». Or le contrôle décisif ne demandait **aucune connaissance du
double-checked locking**, seulement de compter.

C'est précisément le piège que `format_impose` existe pour attraper, et le fait qu'un relecteur technique
attentif y tombe est un indice que l'exemple est bien construit. Un indice, sur un cas.

**Correctif de protocole adopté.** L'annotateur répond désormais **contrôle par contrôle**, quatre valeurs
dans l'ordre, et non par un verdict global. Le verdict en découle mécaniquement, et un contrôle omis
devient visible au lieu d'être absorbé par une impression d'ensemble. Le format d'appel des exemples est
inchangé ; seule la forme de la réponse attendue se resserre.

**Règle de comptage du κ.** Le jugement de **premier passage** est celui qui compte pour l'accord
inter-annotateurs. Une révision faite après avoir vu l'étiquette gonflerait artificiellement le plafond
mesuré. Les deux colonnes restent séparées dans ce journal, et le κ se calculera sur la première.

### État de la relecture au 2026-09-16

- **Accord sur le verdict, premier passage : 3 / 4** — `b03-007` ✅, `b04-015` ✅, `b09-009` ✅,
  `b07-011` ❌ (PASS contre FAIL, révisé après révélation).
- Dont **3 encore dans le golden set** : `b04-015`, `b09-009`, `b07-011`.
- **En attente :** confirmation du contrôle 1 de `b09-009` ; évaluation de `b10-015`.

### Arbitrage du 2026-09-16 — le premier passage de `b07-011` compte dans le κ

L'annotateur a proposé de corriger son premier passage de PASS en FAIL, par crainte « d'introduire une
erreur humaine ». Trois options ont été posées : compter la donnée, l'exclure du κ en documentant
pourquoi, ou la re-mesurer. **Option retenue : la compter.**

Le malentendu à écarter d'abord : l'erreur n'est jamais entrée dans le corpus. `b07-011` est étiqueté FAIL
et l'a toujours été ; le PASS n'existe que dans ce journal, comme **mesure**, jamais comme étiquette.

La raison de fond : le κ inter-annotateurs ne note pas le relecteur, il fixe le **plafond du benchmark**.
Effacer un désaccord dès que l'un des deux se ravise après avoir vu la réponse de l'autre ferait monter ce
κ à 1,0 par construction, et conduirait à conclure que les étiquettes sont parfaitement reproductibles.
Elles ne le sont pas : un relecteur compétent et attentif a lu cet exemple et conclu PASS. C'est un fait
sur la difficulté réelle de la tâche, et il servira à interpréter les sorties du juge fine-tuné — si
celui-ci rend PASS sur un cas analogue, on saura qu'un humain a fait la même lecture.

Réserve consignée, mais non retenue comme motif d'exclusion : ce point de mesure a été recueilli **avant**
le correctif de protocole, quand un verdict global était demandé plutôt que quatre contrôles. Ce format a
pu favoriser une lecture d'ensemble. Il n'a en revanche caché aucune information — la contrainte « trois
points maximum » figurait en toutes lettres dans la requête présentée.

### 5. `b10-015` — premier accord complet, avec une réserve d'amorçage

| | 1 `exactitude` | 2 `absence_de_bugs` | 3 `respect_consignes` | 4 `format_impose` | verdict |
|---|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **F** | **FAIL** |
| étiquette | V | V | V | **F** | **FAIL** |

Accord sur **les quatre contrôles**, pas seulement sur le verdict — le premier du journal. Les motifs
coïncident également : l'annotateur relève « on demande explicitement aucun exemple et il y en a un dans
la réponse », l'étiquette dit « insère un bloc de code avec l'exemple d'en-tête, alors que la requête
imposait de la prose uniquement ». Aucune correction du corpus.

**Réserve sur ce point de mesure : amorçage.** `b10-015` a été présenté immédiatement après `b07-011`,
dont toute la leçon était de vérifier la contrainte de forme. La vigilance de l'annotateur ici n'est donc
pas une lecture pleinement indépendante. Le point compte, mais il vaut moins qu'un accord obtenu à froid.

**Défaut de séquencement, imputable au protocole et non à l'annotateur.** Trois des quatre exemples de la
session 1 — `b04-015`, `b07-011`, `b10-015` — échouent sur un contrôle dédié de format ou de consigne. La
session avait été composée sur le critère « un seul contrôle sépare PASS de FAIL », sans voir que cela
produisait une série homogène, qui apprend au relecteur à chercher toujours le même type de défaut.

**Correctif : entrelacer les types de contrôle fautif** dans les sessions suivantes, de sorte que deux
exemples consécutifs ne partagent pas le même mode d'échec.

### État de la relecture — session 1 close

- **Accord sur le verdict, premier passage : 4 / 5** — `b03-007` ✅, `b04-015` ✅, `b09-009` ✅,
  `b07-011` ❌, `b10-015` ✅.
- Dont **4 dans le golden set actuel** (`b03-007` en est sorti au retirage) : 3 accords sur 4.
- **Aucune correction du corpus n'a été rendue nécessaire par la session 1**, hors la correction de
  périmètre de `respect_consignes` issue des exemples 1 et 2.
- **En attente :** confirmation du contrôle 1 de `b09-009`, seul point resté ouvert.

## Session 2

**Composition revue avant de commencer.** Les six `limite` restants se répartissaient en cinq PASS sans
aucun contrôle fautif et un seul FAIL. Les présenter dans l'ordre du bucket aurait reproduit en pire le
défaut relevé en session 1 : après trois PASS consécutifs, le verdict devient prévisible par la position
et les items suivants ne mesurent plus rien. La session 2 est donc tirée sur **l'ensemble du golden set**,
en alternant les verdicts et les contrôles fautifs, au lieu de vider le bucket `limite`.

### 6. `b12-008` — accord complet, non confondu

| | 1 `contexte_pertinent` | 2 `contexte_suffisant` | 3 `bruit_maitrise` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | **F** | V | **FAIL** |
| étiquette | V | **F** | V | **FAIL** |

Second accord consécutif sur tous les contrôles, et le premier qui ne souffre d'aucune réserve
d'amorçage : tâche `RAG_CONTEXT_RELEVANCE` jamais rencontrée dans la relecture, mode d'échec inédit,
aucun exemple antérieur n'orientait vers la suffisance. Les motifs coïncident — l'annotateur relève qu'il
« manque encore quelques infos pour répondre de façon pertinente », l'étiquette que l'ordre de fusion
demandé reste absent faute de corps de méthode.

Le point remarquable est le **placement** du défaut : sur la suffisance et non sur la pertinence. C'est
la distinction que ces trois critères servent précisément à séparer, et la partie difficile de l'item —
le contexte est manifestement pertinent, ce qui invite à le valider en bloc. Aucune correction du corpus.

### État de la relecture

- **Accord sur le verdict, premier passage : 5 / 6** — seul `b07-011` reste en désaccord.
- **Désaccord au niveau contrôle : 1**, sur `b09-009`, tranché en faveur de l'annotateur et corrigé
  dans le corpus.
- Aucune correction du corpus rendue nécessaire par la session 2 à ce stade.

### 7. `b06-013` — accord complet sur une consigne facultative

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Troisième accord consécutif sur tous les contrôles. L'item se joue sur une omission réelle — la réponse
ne dit rien du passage à l'échelle derrière un répartiteur de charge, ni affinité de session, ni diffusion
multi-instances, ni bus de messages — mais la requête introduisait cette demande par « si tu as le temps ».
`respect_consignes` ne portant que sur les consignes obligatoires, l'omission ne fait pas échouer l'item.
Les sept affirmations techniques vérifiables sont exactes. Aucune correction du corpus.

**Réserve méthodologique sur ce point de mesure : chemin non observé.** L'annotateur a répondu « VVV, Pass »
sans motif. Un PASS obtenu en voyant la demande facultative et en jugeant correctement qu'elle n'engage pas,
et un PASS obtenu en ne remarquant pas qu'il y avait une seconde partie, produisent la même case. L'accord
est réel, mais il ne démontre pas la maîtrise de la notion de consigne facultative.

**Correctif de protocole : demander une ligne de motif sur les items jugés PASS.** Sur les FAIL, la
formulation spontanée de l'annotateur (« ça Fail car… ») lève déjà l'ambiguïté ; c'est sur les PASS que le
raisonnement reste invisible, et ce sont précisément les items où une inattention se confond avec un accord.

### État de la relecture

- **Accord sur le verdict, premier passage : 6 / 7** — seul `b07-011` reste en désaccord.
- **Désaccord au niveau contrôle : 1**, sur `b09-009`, tranché en faveur de l'annotateur et corrigé.
- Trois accords complets consécutifs : `b10-015` (amorcé), `b12-008` (non confondu), `b06-013`
  (chemin non observé).

### 8. `b02-001` — accord complet sur une injection SQL

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | **F** | V | **FAIL** |
| étiquette | V | **F** | V | **FAIL** |

Quatrième accord consécutif sur tous les contrôles, motif à l'appui : « il y a un risque d'injection SQL ».
L'étiquette dit la même chose — requête construite par interpolation de chaîne, CWE-89. `exactitude_technique`
est correctement laissé à V : les six affirmations annexes de la réponse sont vraies, `rowcount` à `-1` sur un
`SELECT` sqlite3 compris. Sur un item de ce genre, la tentation est de tout noircir une fois la faille repérée.
Aucune correction du corpus.

**Nuance sans effet sur l'étiquette.** Le raisonnement de référence relève une seconde conséquence non
mentionnée par l'annotateur : le même code lève `sqlite3.OperationalError` sur une donnée légitime contenant
une apostrophe (`o'brien@example.com`). Faille de sécurité et bug de correction tombent tous deux dans
`absence_de_bugs`, la case est donc identique et l'accord entier.

**Mise en garde sur la lecture de la série.** `b02-001` est un cas `defaillant`, classé trivialement séparable
par le relevé ci-dessous. Ce point confirme la calibration de l'annotateur, il ne la met pas à l'épreuve.

### Relevé : la difficulté restante est concentrée sur quatre items

Sur les 44 items du golden set non encore relus, `cas` prédit le verdict presque parfaitement — les 21 FAIL
sont tous `defaillant`, et 19 des 23 PASS sont `parfait`. Les seuls items conservant une difficulté réelle
sont les quatre `limite` encore PASS : `b03-012`, `b05-008`, `b07-015`, `b13-013`.

**Conséquence pour la relecture :** le κ inter-annotateur finira près de 1 sans que ce soit informatif.

**Conséquence pour le benchmark, plus sérieuse :** si 44 items sur 50 sont trivialement séparables, le 14B
et le 32B y marqueront tous deux très haut et la comparaison manquera de résolution — c'est précisément la
question que le protocole doit trancher. À traiter avant le fine-tuning, proposition chiffrée à établir.

### État de la relecture

- **Accord sur le verdict, premier passage : 7 / 8** — seul `b07-011` reste en désaccord.
- **Désaccord au niveau contrôle : 1**, sur `b09-009`, tranché en faveur de l'annotateur et corrigé.

### 9. `b05-008` — accord complet sur un item difficile, motif plus juste que l'étiquette

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Cinquième accord consécutif, et le premier obtenu sur un des quatre items à difficulté réelle : `limite`,
**verbeux**, cinq sections dont une rubrique « alternatives » non demandée — exactement le profil qui
déclenche un rejet réflexe pour cause de longueur. L'annotateur ne l'a pas suivi. Aucune correction du corpus.

**Point où le motif de l'annotateur dépasse l'étiquette.** L'étiquette qualifie les chiffres de « du bon
ordre » ; l'annotateur écrit « exacts pour CPython ». Mesure faite sur CPython 3.12.0 :

```
avec __dict__  : objet 48 + dict 296 = 344 octets
avec __slots__ : objet 48 octets            facteur 7,2
sur 5 M d'instances : 1,48 Go          réponse : ~1,5 Go
```

Les 344 et 48 octets annoncés tombent à l'octet près, et l'extrapolation aussi. L'auteur de l'étiquette
soupçonnait de surcroît, avant de mesurer, que 344 était un chiffre hérité de billets anciens et trop élevé
pour un CPython récent : la mesure a corrigé l'auteur, pas l'annotateur. **Leçon : la couverture prudente
(« du bon ordre ») n'est pas gratuite — elle masque une vérification qui était à portée de trois lignes.**

**Nuance mesurée.** `getsizeof(obj.__dict__)` matérialise le dictionnaire, alors que depuis CPython 3.11 les
attributs résident d'abord dans un tableau géré converti en `dict` seulement à l'accès. Une instance qui ne
touche jamais `__dict__` coûte donc moins que 344 octets — mais les 48 octets de l'objet ne comptent pas non
plus ce tableau. Les deux écarts se compensent grossièrement et le facteur annoncé tient. Sans effet sur l'étiquette.

### État de la relecture

- **Accord sur le verdict, premier passage : 8 / 9** — seul `b07-011` reste en désaccord.
- **Désaccord au niveau contrôle : 1**, sur `b09-009`, tranché en faveur de l'annotateur et corrigé.
- Items à difficulté réelle traités : 1 sur 4 (`b05-008`). Restent `b03-012`, `b07-015`, `b13-013`.

### 10. `b13-012` — accord sur le verdict, désaccord sur `citations_exactes`

| | 1 `affirmations_etayees` | 2 `absence_invention` | 3 `citations_exactes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | F | F | **F** | **FAIL** |
| étiquette | F | F | **V** | **FAIL** |

Premier item `RAG_FAITHFULNESS` de la relecture. Accord entier sur le fond — l'interface `Assistant`, ses
deux signatures et le type `TokenStream` sont intégralement absents du contexte — et motif identique.
Le désaccord porte sur le seul contrôle 3. Aucune correction du corpus.

**Convention vérifiée sur l'ensemble du corpus, non inventée pour l'occasion.** Sur les onze items
`RAG_FAITHFULNESS` où `affirmations_etayees` et `absence_invention` sont tous deux faux,
`citations_exactes` vaut **V dix fois et F une seule**. L'unique F, `b12-014`, est le cas qui justifie la
règle : cette sortie ne se contente pas d'inventer, elle **fabrique une citation** —
`OllamaService -[IMPLEMENTS]-> PersistentStateComponent<OllamaService.State>` — alors que l'arête réelle
porte `OllamaSettings` des deux côtés, y compris dans le paramètre de type. Elle présente donc un extrait
réécrit comme preuve vérifiable.

**Règle retenue :** `citations_exactes` ne sanctionne que la déformation de matériau réellement puisé dans
le contexte. Quand la sortie ne cite ni ne paraphrase rien du contexte, le contrôle est vrai par vacuité.

**Justification de conception.** Si l'invention faisait également tomber le contrôle 3, celui-ci serait
strictement impliqué par le contrôle 2 et n'apporterait jamais d'information. Le corpus perdrait la
distinction entre « invente » et « invente et maquille une preuve », qui est le degré au-dessus : le lecteur
y est invité à vérifier et croit trouver confirmation. La convention inverse reste tenable, au prix de la
réécriture de dix items et de la fusion de fait des contrôles 2 et 3. Position de l'annotateur consignée.

### État de la relecture

- **Accord sur le verdict, premier passage : 9 / 10** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009`, tranché en faveur de l'annotateur et corrigé dans le
  corpus, et `b13-012`, où l'étiquette est maintenue, convention documentée à l'appui.
- Items à difficulté réelle traités : 1 sur 4. Restent `b03-012`, `b07-015`, `b13-013`.

### 11. `b07-015` — accord complet, et découverte d'une fuite déterministe

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Sixième accord consécutif sur tous les contrôles. L'item se joue sur l'articulation exacte entre attente
exponentielle et gigue — l'exponentielle seule espace les vagues sans les désynchroniser — et sur une demande
non traitée, le disjoncteur, introduite par « si tu as le temps ». Aucune correction du corpus.

**Réserve d'amorçage.** C'est le deuxième item de la relecture dont le point de bascule est une consigne
facultative, après `b06-013`, et le motif de l'annotateur porte sur ce seul aspect. La règle appliquée est la
bonne, mais un annotateur ayant retenu le raccourci de surface produirait la même réponse.

### Fuite mesurée : la consigne facultative prédit parfaitement le verdict

Balayage des 200 requêtes du corpus sur les tournures facultatives (« si tu as le temps », « si possible »,
« éventuellement », « facultat… ») :

```
17 items portent une consigne facultative
  cas      : limite  17 / 17
  verdicts : PASS    17 / 17
  formule  : « Si tu as le temps » dans 15 des 17
```

**Zéro contre-exemple.** Contrairement au biais de verbosité, corrélation statistique qu'il fallait éprouver
par test de permutation, celle-ci est **déterministe** : aucun test n'est nécessaire, la règle de surface
classe les 17 items sans erreur. Un juge n'a donc jamais besoin d'acquérir la notion de consigne facultative —
détecter la chaîne suffit, et c'est le raccourci qu'un modèle apprend en premier, étant plus simple que la
règle visée.

Ces 17 items représentent par ailleurs 17 des 40 `limite` du corpus, soit la catégorie censée porter la
difficulté.

**Correctif pressenti, à chiffrer avant d'être proposé :** introduire des items portant une consigne
facultative mais dont le verdict est FAIL pour une raison sans rapport — affirmation fausse, bug — de façon à
briser la corrélation sans toucher aux 17 existants, et diversifier les formulations. Reste à établir leur
répartition entre `train` et le golden set : si le golden en contient plusieurs, le benchmark est touché
autant que l'entraînement.

### État de la relecture

- **Accord sur le verdict, premier passage : 10 / 11** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012` (étiquette maintenue).
- Items à difficulté réelle traités : 2 sur 4. Restent `b03-012`, `b13-013`.

### Correctif de la fuite « consigne facultative » — exécuté

Le correctif esquissé à la fiche `b07-015` a été mené en trois lots, sans créer ni supprimer aucun exemple
et sans déplacer un seul verdict.

| lot | contenu | items |
|---|---|---|
| 1 | diversification des formulations : les 15 « Si tu as le temps » deviennent six tournures | 12 réécritures |
| 2 | clause facultative ajoutée à des FAIL existants, `<thinking>` repris à chaque fois | 12 (3 golden, 2 valid, 7 train) |
| 3 | items où le volet facultatif est réellement **traité** | 3 |

**Résultat mesuré.** La règle de surface « requête à clause facultative ⇒ PASS » passe de **17/17 (100 %)** à
**17/30 (57 %)** sur le corpus et **3/6 (50 %)** sur le golden set, où elle ne vaut donc plus mieux qu'une
pièce lancée.

**Le lot 3 répond à un second raccourci**, distinct de la corrélation et plus insidieux : dans les 17 items
d'origine, la clause facultative était *toujours ignorée* par la réponse. Un juge pouvait donc apprendre
« une clause facultative est là pour être sautée » sans acquérir la notion. Les trois formes manquantes :
`b02-008` traite les jours correctement et reste PASS ; `b06-009` traite les `Map` correctement et reste
PASS ; `b10-011` traite `Cleaner` **faussement** — il lui prête l'exécution des actions à l'arrêt de la
machine virtuelle, garantie inexistante — et le défaut tombe sur `exactitude_technique`, non sur
`respect_consignes`, puisque la demande était facultative : c'est son contenu qui est faux, pas son omission.

**Cinq candidats ont été refusés par le script plutôt que corrompus** : `b03-001` partage sa `consigne` avec
une paire contrastive, et `b05-014`, `b06-005`, `b06-011`, `b07-012` traitaient déjà le sujet de la clause
dans leur réponse, où la phrase « non traitée » aurait été fausse.

**Invariants après correctif :** 200 exemples, 0 erreur de validation, 104 PASS / 96 FAIL, golden 24/26,
tirage inchangé. Les onze relectures déjà faites restent valides.

### 12. `b08-004` — accord complet sur un contrôle dédié de dépendance

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | 4 `aucune_dependance_externe` | verdict |
|---|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **F** | **FAIL** |
| étiquette | V | V | V | **F** | **FAIL** |

Septième accord consécutif sur tous les contrôles, motif à l'appui : « le code est bon mais pydantic n'est
pas dans la stdlib ». Aucune correction du corpus.

L'item se joue sur l'articulation entre les contrôles 3 et 4. Le code écrit est valide — syntaxe Pydantic v2
correcte, `field_validator` avec `@classmethod`, `default_factory` évitant le partage de liste — donc les
contrôles 1 et 2 tiennent. La contrainte « bibliothèque standard uniquement » est une consigne de la requête,
mais elle dispose d'un contrôle dédié, de sorte qu'elle ne retombe pas sur `respect_consignes`. L'annotateur
a placé le défaut au seul endroit prévu pour lui et laissé les trois autres intacts.

**Ce point valide la correction de périmètre décidée aux exemples 1 et 2 de la session 1.** Sans la formule
`RESPECT_CONSIGNES_PERIMETRE_REDUIT`, ce même item aurait légitimement pu recevoir deux F pour un seul
défaut, et le corpus aurait enseigné un double comptage.

### État de la relecture

- **Accord sur le verdict, premier passage : 11 / 12** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012`
  (étiquette maintenue, convention documentée).
- Items à difficulté réelle traités : 2 sur 4. Restent `b03-012` et `b13-013`.

### 13. `b03-012` — accord complet, et une erreur de présentation qui en réduit la portée

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Huitième accord consécutif. Les sept affirmations vérifiables sont exactes, `--force-with-lease` compris,
et le motif coïncide : « le `--onto` est sans obligation donc pas bloquant ». Aucune correction du corpus.

**Réserve, imputable au présentateur.** Cet item devait établir que l'annotateur applique la *notion* de
consigne facultative et non la chaîne « si tu as le temps », puisque sa formulation avait été réécrite en
« sans obligation » au lot 1. Mais la présentation annonçait explicitement cette réécriture et précisait que
« l'item teste donc la notion ». L'annotateur a donc été informé de ce qu'il fallait chercher. Le point
demeure un accord ; il ne démontre plus la généralisation visée.

C'est la troisième réserve de cette nature, après `b10-015` et `b07-015`. **Correctif : ne plus indiquer, en
présentant un item, ce qu'il est censé tester.** La difficulté doit rester à découvrir.

### Échantillon aléatoire des items faciles — tiré le 2026-09-17, graine 17

Tiré parmi les 37 items du golden set ni relus ni classés difficiles, et **commité avant relecture du
premier d'entre eux**, pour la même raison que le pré-enregistrement : sans tirage figé d'avance, rien
n'empêche de choisir au fil de l'eau les items faciles qui arrangent.

| item | verdict | cas | tâche |
|---|---|---|---|
| `b04-014` | FAIL | defaillant | explication |
| `b07-005` | PASS | parfait | debogage |
| `b07-008` | FAIL | defaillant | debogage, verbeux |
| `b08-007` | PASS | parfait | debogage |
| `b08-011` | FAIL | defaillant | question_reponse |
| `b09-006` | FAIL | defaillant | generation |
| `b09-014` | PASS | parfait | explication |
| `b13-003` | FAIL | defaillant | retrieval (RAG_CONTEXT_RELEVANCE) |

5 FAIL / 3 PASS, proche de la proportion du golden set. **Objet du sondage :** vérifier que ces items sont
aussi séparables que leur `cas` le prétend. Un désaccord sur deux d'entre eux invaliderait l'affirmation
« le reste du golden set est trivial » et imposerait d'élargir la relecture.

### État de la relecture

- **Accord sur le verdict, premier passage : 12 / 13** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012`
  (étiquette maintenue).
- Items à difficulté réelle traités : **3 sur 4**. Reste `b13-013`.

### 14. `b13-003` — accord complet, sur un point de mesure compromis

| | 1 `contexte_pertinent` | 2 `contexte_suffisant` | 3 `bruit_maitrise` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | F | F | F | **FAIL** |
| étiquette | F | F | F | **FAIL** |

Neuvième accord consécutif. Contraste net avec `b12-008`, où seule la suffisance tombait : ici les trois
contrôles échouent, aucun extrait ne portant sur l'interface visée. Aucune correction du corpus.

**Point de mesure compromis, signalé à l'annotateur avant sa réponse.** `b13-003` partage son contexte et sa
requête avec `b13-012`, déjà relu : mêmes cinq extraits, même question. L'annotateur avait donc déjà établi
que rien n'y concerne l'interface `Assistant`. Les deux items appartiennent à la même famille — le
regroupement par contexte d'extraction les fait voyager ensemble dans le tirage, ce qui explique leur
présence commune dans le golden set.

L'item **n'a pas été échangé** contre un autre : le tirage avait été figé et commité précisément pour
interdire de remplacer un item devenu gênant.

**Conséquence à retenir pour la composition des sessions :** deux items d'une même famille RAG ne doivent
pas être présentés à la suite, l'analyse du premier réglant le second.

### 15. `b07-005` — accord complet, premier item de l'échantillon aléatoire

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Dixième accord consécutif. Le motif de l'annotateur couvre les deux moitiés de l'item : le diagnostic
d'épuisement du générateur, et la vérification que les deux corrections proposées sont elles-mêmes sans bug.
C'est le piège propre à ce type d'exemple — valider l'explication et omettre de relire le code correctif.
Aucune correction du corpus.

**Premier point de l'échantillon aléatoire, et il se comporte comme prévu :** accord immédiat sur un item
`parfait`, sans information sur la calibration de l'annotateur. C'est précisément ce qu'un sondage doit
produire si l'hypothèse « le reste du golden set est trivialement séparable » est vraie. Ces points valent
par leur accumulation, pas individuellement : c'est un désaccord qui serait informatif ici, pas un accord.

### État de la relecture

- **Accord sur le verdict, premier passage : 14 / 15** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012`
  (étiquette maintenue).
- Items à difficulté réelle traités : 3 sur 4. Reste `b13-013`.
- Échantillon aléatoire : 1 sur 8 relu.

### 16. `b09-006` — accord complet, et première validation indépendante d'un rétrofit

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | F | F | F | **FAIL** |
| étiquette | F | F | F | **FAIL** |

Onzième accord consécutif, motif identique jusqu'au mécanisme : `RetentionPolicy.CLASS` conserve
l'annotation dans le `.class` mais la machine virtuelle ne la charge pas, `isAnnotationPresent` renvoie
`false`, et l'intercepteur ne journalise jamais rien, en silence. Aucune correction du corpus.

Deux finesses tranchées correctement sans commentaire. **L'affirmation 3 de la réponse est vraie** — `CLASS`
est bien la rétention par défaut : la réponse énonce un fait exact et s'en sert pour justifier un choix qui
rend le dispositif inopérant, et l'annotateur n'a pas laissé le fait juste sauver le raisonnement faux.
**`respect_consignes` tombe** parce que la requête exigeait explicitement une détection « à l'exécution »,
consigne obligatoire violée, distincte du défaut technique.

**Validation indépendante du lot 2.** `b09-006` est l'un des douze items rétrofités quelques heures plus
tôt : sa clause « Accessoirement, dis un mot de `@Inherited` » a été ajoutée par le correctif de fuite, et
la réponse ne la traite pas. L'annotateur, qui ignorait que cet item avait été modifié, n'en a pas fait
état — correctement, la clause étant facultative. C'est la première vérification par un tiers non informé
que la clause ajoutée ne dérègle pas le jugement et ne détourne pas l'attention du défaut réel.

### État de la relecture

- **Accord sur le verdict, premier passage : 15 / 16** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012`
  (étiquette maintenue).
- Items à difficulté réelle traités : 3 sur 4. Reste `b13-013`.
- Échantillon aléatoire : 2 sur 8 relus, 2 accords.

### 17. `b09-014` — accord complet sur la hiérarchie des exceptions

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Douzième accord consécutif. Aucune correction du corpus.

Le point piégeux de l'item est l'affirmation 7 : `KeyboardInterrupt` et `SystemExit` dérivent de
`BaseException` et non d'`Exception`, de sorte qu'`except Exception` les laisse passer là où un `except:`
nu les intercepte. La réponse la rend exactement, et l'annotateur l'a relevée explicitement dans son motif
— c'est la vérification qui distingue une lecture attentive d'un accord de principe sur une réponse bien
écrite et bien structurée.

### État de la relecture

- **Accord sur le verdict, premier passage : 16 / 17** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012`
  (étiquette maintenue).
- Items à difficulté réelle traités : 3 sur 4. Reste `b13-013`.
- **Échantillon aléatoire : 3 sur 8 relus, 3 accords.** L'hypothèse « le reste du golden set est
  trivialement séparable » n'est pas contredite à ce stade.

### 18. `b07-008` — accord complet sur un fait exact au service d'une conclusion fausse

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | F | F | V | **FAIL** |
| étiquette | F | F | V | **FAIL** |

Treizième accord consécutif, et l'annotateur nomme le bon vecteur : `<img src=x onerror=alert(1)>` traverse
le filtre par expression régulière sans rencontrer un seul `<script>`. Aucune correction du corpus.

**Structure de l'item, identique à `b09-006`.** L'affirmation 3 est **vraie** — une balise `<script>`
insérée via `innerHTML` n'est pas exécutée, la spécification le prévoit. Ce qui est faux, c'est l'inférence
4 qu'on en tire (« le vecteur est donc largement neutralisé ») et la correction 5 qui en découle. Deux items
du golden set partagent donc cette forme : un fait exact mis au service d'une conclusion dangereuse.
`respect_consignes` reste à V, la requête demandant d'expliquer et de corriger — les deux ont été tentés.

### Décision de méthode : l'annotateur peut et doit vérifier

Question posée par l'annotateur à cet item : est-il légitime de faire des recherches pour répondre ?

**Oui, et c'est requis**, depuis que le golden set a changé de rôle. Tant que la relecture était un sondage
de contrôle des étiquettes, la recherche aurait biaisé la mesure. Mais le golden set sert désormais
d'**étalon de référence** à toutes les variantes, y compris à un juge extérieur au corpus : un étalon doit
être juste, pas rapide, et une étiquette de référence devinée ne vaut rien.

**Seule interdiction : consulter l'étiquette ou le `<thinking>` de référence avant d'avoir répondu.**
Vérifier un fait technique est légitime ; lire le raisonnement de référence détruirait l'indépendance.

**À déclarer dans le REX :** le κ mesure alors l'accord entre une étiquette rédigée par un LLM et un expert
humain disposant de temps et d'un moteur de recherche. C'est la comparaison pertinente pour un étalon, et
elle doit être écrite explicitement plutôt que sous-entendue.

### Nouvelle donnée collectée : « vérifié » contre « de tête »

Le champ `cas` (`parfait` / `limite` / `defaillant`) a été attribué a priori par l'auteur des étiquettes, et
le relevé a montré qu'il prédit le verdict presque parfaitement — il mesure donc mal la difficulté réelle.
Le signalement par l'annotateur d'avoir dû vérifier un point constitue une **mesure de difficulté
indépendante et humaine**, à collecter sur les items restants d'un mot (« vérifié » / « de tête »).

Elle alimentera la métrique secondaire n°4 du pré-enregistrement — justesse sur la strate difficile —
aujourd'hui adossée à un `cas` peu fiable.

### État de la relecture

- **Accord sur le verdict, premier passage : 17 / 18** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009` (corrigé), `b13-012` (étiquette maintenue).
- Items à difficulté réelle traités : 3 sur 4. Reste `b13-013`.
- Échantillon aléatoire : 4 sur 8 relus, 4 accords.

### Report de `b13-013`, et limite de famille dans le golden set

`b13-013`, dernier item classé difficile, partage sa famille `rag-ctx-assistant-neo4j` et son contexte
(empreinte `8559f10c33bf`) avec `b13-012` et `b13-003`, tous deux déjà relus. La règle inscrite à la fiche
`b13-003` interdit de l'enchaîner : il est reporté, et **restera compromis quel que soit le moment où il
sera présenté**, l'annotateur ayant déjà analysé ce contexte deux fois. Il sera relu malgré tout, en tant
que dernier item difficile, avec la réserve consignée.

Le golden set contient donc **trois items adossés à un unique contexte RAG**. C'est l'effet voulu du
regroupement par famille, qui supprime la fuite de contexte entre entraînement et test ; le prix en est une
corrélation entre items de test, consignée en addendum daté du pré-enregistrement.

### 19. `b08-007` — accord complet sur la pollution de prototype

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Quatorzième accord consécutif. Aucune correction du corpus.

Le motif de l'annotateur touche le point subtil de l'item sans avoir eu à le chercher : « issue de
`JSON.parse` ». C'est exactement ce qui rend l'affirmation 2 vraie — `JSON.parse` crée `__proto__` comme
propriété **propre et énumérable**, donc visible par `Object.keys`, là où un littéral d'objet passerait par
l'accesseur et ne produirait aucune clé. Sans cette particularité, l'attaque décrite ne fonctionnerait pas,
et la correction proposée n'aurait pas d'objet.

Signal de difficulté (« vérifié » / « de tête ») : **non renseigné** pour cet item.

### État de la relecture

- **Accord sur le verdict, premier passage : 18 / 19** — seul `b07-011` reste en désaccord.
- **Désaccords au niveau contrôle : 2** — `b09-009` (corrigé), `b13-012` (étiquette maintenue).
- Items à difficulté réelle traités : 3 sur 4. Reste `b13-013`, reporté et compromis.
- **Échantillon aléatoire : 5 sur 8 relus, 5 accords.**

### 20. `b08-011` — le désaccord qui a révélé une fuite de mon fait

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | F | F | **F** | **FAIL** |
| étiquette | F | F | **V** | **FAIL** |

Accord sur le verdict, et l'analyse de fond de l'annotateur dépasse l'étiquette : `NoClassDefFoundError`
dérive de `LinkageError` et signale un échec de résolution lors de la liaison sur une classe présente à la
compilation, tandis que `ClassNotFoundException` provient d'un chargement dynamique explicite
(`Class.forName`, `loadClass`). Le « distinguo historique » de la réponse est une invention.

**Le désaccord sur le contrôle 3 n'est pas un écart de l'annotateur : il a révélé un défaut du corpus.**
Le motif invoquait l'omission de la clause facultative, alors que la convention veut qu'une omission
facultative n'entre pas dans `respect_consignes` — règle que l'annotateur avait appliquée correctement
quatre fois. La cause était que `b08-011` est un item rétrofité, dont la clause avait été placée **en
paragraphe séparé** au lieu d'une incise, ce qui la fait lire comme une seconde exigence.

Mesure consécutive : les 17 items d'origine portaient tous la clause en incise et étaient tous PASS, les 13
rétrofits la portaient tous en paragraphe isolé et étaient tous FAIL — une fuite déterministe à **30/30**,
créée en corrigeant celle à 17/17. Détail complet au chantier 9 de `AUDIT.md`.

**Étiquette maintenue à V sur le contrôle 3**, la convention étant inchangée. Le premier passage de
l'annotateur est consigné tel quel, et la cause du désaccord est portée au débit du corpus, non au sien.

### État de la relecture

- **Accord sur le verdict, premier passage : 19 / 20.**
- **Désaccords au niveau contrôle : 3** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012`
  (étiquette maintenue, convention documentée), `b08-011` (étiquette maintenue, corpus corrigé).
- Échantillon aléatoire : 6 sur 8 relus. Reste `b04-014`, puis `b13-013` reporté.

### 21. `b13-013` — accord complet sur une abstention, dernier item difficile

| | 1 `affirmations_etayees` | 2 `absence_invention` | 3 `citations_exactes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Quinzième accord consécutif, et **les quatre items à difficulté réelle sont désormais couverts**
(`b05-008`, `b07-015`, `b03-012`, `b13-013`). Aucune correction du corpus.

Le motif de l'annotateur nomme le pivot de l'item : l'abstention est « justifiée à partir des extraits
disponibles ». C'est ce qui sauve `affirmations_etayees` — une abstention n'est pas étayée d'office, elle
l'est ici parce que l'inventaire des cinq extraits est exact et vérifiable point par point.

**Paire pédagogique avec `b13-012`, sur un contexte identique.** Là, la sortie fabriquait l'interface
entière et échouait ; ici, elle écarte explicitement `ConversationMessage.assistant(String)` comme homonyme
trompeur au lieu de l'exploiter. Le corpus enseigne donc les deux faces de la même situation : ce que la
corrélation de familles coûte en indépendance statistique, elle le rapporte en valeur d'apprentissage.

**Réserve maintenue :** troisième item bâti sur ce contexte, après `b13-012` et `b13-003`. Point de mesure
compromis, signalé à l'annotateur avant sa réponse.

### État de la relecture

- **Accord sur le verdict, premier passage : 20 / 21.**
- **Désaccords au niveau contrôle : 3** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012` et
  `b08-011` (étiquettes maintenues).
- **Items à difficulté réelle : 4 sur 4, terminés.**
- Échantillon aléatoire : 7 sur 8. Reste `b04-014`, dernier item avant le calcul du κ.

### 22. `b04-014` — accord sur le verdict, désaccord de contrôle identique à `b08-011`

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | F | F | **F** | **FAIL** |
| étiquette | F | F | **V** | **FAIL** |

Sur le fond, accord entier : la réponse inverse la règle d'idempotence de la RFC 9110 — `PUT` **est**
idempotent, `POST` ne l'est pas — et le conseil final, rejouer les `POST` et bloquer les `PUT`, est dangereux
à l'envers. Aucune correction du corpus.

**Le troisième F invoque à nouveau l'omission d'une demande facultative**, comme à `b08-011`. Mais
l'explication retenue là-bas ne s'applique plus : `b04-014` est un item rétrofité **dont la clause a été
remise en incise** au correctif du chantier 9. Elle se lit désormais comme celles des items d'origine, donc
le placement n'est plus en cause.

Deux lectures soumises à l'annotateur, aux conséquences opposées : soit il **énumère** les griefs sur un item
déjà FAIL sans les attribuer à un contrôle précis — cohérent avec ses six items PASS, où aucune omission
facultative n'a jamais fait basculer un verdict, et sans conséquence sur le corpus ; soit il **récuse la
convention**, et il faut alors réécrire une dizaine d'items et la règle de `PROTOCOLE.md`. **Réponse en
attente ; l'étiquette n'est pas modifiée entre-temps.**

---

## κ inter-annotateur — calculé le 2026-09-17 sur 21 items

```
items relus du golden set : 21 / 50  (42 %)
accord observé sur le verdict : 20/21 = 95,2 %
κ de Cohen : 0,901        IC 95 % bootstrap [0,674 — 1,000]

matrice de confusion (verdict)
  annotateur PASS / étiquette PASS : 8
  annotateur PASS / étiquette FAIL : 1     (b07-011)
  annotateur FAIL / étiquette PASS : 0
  annotateur FAIL / étiquette FAIL : 12
```

`b03-007` est exclu du calcul : relu avant le retirage, il ne fait plus partie du golden set.

**Lecture honnête de ces chiffres.**

1. **L'intervalle est large.** La borne basse à 0,674 interdit d'affirmer un accord « quasi parfait » plutôt
   que « substantiel ». C'est la limite de puissance prévue au pré-enregistrement ; porter la relecture à 50
   items resserrerait l'intervalle d'environ moitié.
2. **Le κ sur le verdict flatte.** L'accord **complet, contrôle par contrôle**, vaut **16/21 = 76 %** :
   4 items portent au moins un désaccord de contrôle (`b09-009`, `b13-012`, `b08-011`, `b04-014`). Le verdict
   est robuste, l'attribution du défaut au bon contrôle l'est nettement moins. C'est ce second chiffre qui
   doit figurer en premier dans le REX.
3. **Trois des quatre écarts portent sur le même point** — l'imputation d'une omission facultative à
   `respect_consignes` — donc il s'agit d'un désaccord unique répété, non de quatre erreurs indépendantes.
4. **Ce κ est un majorant.** Les items sont présentés à l'annotateur avec les affirmations déjà isolées dans
   un tableau, ce qui constitue une aide réelle. Un annotateur lisant la sortie brute ferait vraisemblablement
   moins bien. À déclarer dans le REX.

### État de la relecture

- **21 items relus sur 50**, accord verdict 20/21, accord complet 16/21.
- **Items à difficulté réelle : 4 sur 4, terminés.**
- **Échantillon aléatoire : 8 sur 8, terminé** — aucun désaccord de verdict. L'hypothèse « le reste du golden
  set est trivialement séparable » n'est pas contredite.
- En attente : arbitrage de l'annotateur sur la convention de `respect_consignes`.

---

## Arbitrage à froid — 2026-09-18

**Question posée** (reportée de la veille, à dessein) : sur `b08-011` et `b04-014`, l'annotateur avait marqué
`respect_consignes` faux en invoquant l'omission d'une demande introduite par « Accessoirement » / « En
bonus ». Énumération de griefs sur un item déjà FAIL, ou récusation de la convention ?

**Réponse, rendue en début de séance et non en fin :** erreur d'inattention. La convention est confirmée —
une demande facultative ignorée n'entre pas dans `respect_consignes`.

**Conséquences.**

- **Aucune modification du corpus.** Les deux étiquettes sont maintenues, la convention de `PROTOCOLE.md`
  est inchangée, et la dizaine d'items qu'une récusation aurait imposé de réécrire est épargnée.
- **Les premiers passages restent consignés tels quels.** Ils comptent pour le κ, fatigue comprise :
  l'accord complet contrôle par contrôle demeure **16/21 = 76 %**, et l'accord verdict **20/21**. Corriger
  rétroactivement le premier passage donnerait un chiffre flatteur et faux.
- **Les trois désaccords de contrôle sur `respect_consignes` sont donc un désaccord unique répété**, dû à
  l'inattention et non à une divergence de fond. À dire tel quel dans le REX.

**Ce que cet arbitrage valide, au-delà de son contenu.** Le protocole à deux colonnes — premier passage pour
le κ, arbitrage à froid pour l'étiquette — a été adopté la veille en réponse à la question « la fatigue de
l'annotateur est-elle un aléa acceptable ? ». C'est sa première mise à l'épreuve, et elle confirme la
distinction : le même relecteur, sur le même item, a jugé différemment selon son état, et c'est le passage à
froid qui fixe l'étalon tandis que le passage fatigué reste dans la mesure de reproductibilité.

## Session 3 — reprise pendant l'entraînement du 14B

### 23. `b02-002` — accord complet, point non indépendant

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Accord sur les trois contrôles et le verdict. Motif concordant : requête paramétrée, API `sqlite3`
standard, ni bug ni injection. Aucune correction du corpus.

**Réserve : point non indépendant.** `b02-002` forme une paire contrastive avec `b02-001`, déjà relu,
dont il partage l'énoncé mot pour mot — l'annotateur y avait jugé la version vulnérable à l'injection.
Divulgué avant sa réponse. Même traitement que `b13-003` et `b13-013`.

### État de la relecture

- **Accord sur le verdict, premier passage : 21 / 22.**
- **Désaccords au niveau contrôle : 3** — `b09-009` (corrigé en faveur de l'annotateur), `b13-012` et
  `b08-011` (étiquettes maintenues ; l'arbitrage à froid du 2026-09-18 a confirmé la convention).
- **22 items relus sur 50**, 28 restants.

### 24. `b07-002` — accord complet sur un interblocage par verrous croisés

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | F | F | V | **FAIL** |
| étiquette | F | F | V | **FAIL** |

Seizième accord consécutif sur tous les contrôles. Le motif de l'annotateur — « le vrai problème est un
interblocage par verrous croisés » — nomme exactement ce que l'étiquette développe : un verrou équitable
ordonne les prétendants à un même verrou, il ne supprime pas la dépendance circulaire entre deux verrous
distincts. Aucune correction du corpus.

`respect_consignes` correctement laissé à V : la requête demandait d'expliquer et de corriger, les deux
ont été tentés.

**Nuance sans effet sur les cases.** L'étiquette relève un second défaut que le motif de l'annotateur ne
mentionne pas : le code proposé supprime bien l'interblocage, mais en remplaçant les verrous par instance
par un verrou unique global, ce qui sérialise tous les virements du service et échange le gel contre un
goulot d'étranglement — précisément sous la charge qui motivait la question. Les deux défauts relèvent de
`absence_de_bugs`, la case est donc identique.

### État de la relecture

- **Accord sur le verdict, premier passage : 22 / 23.**
- **Désaccords au niveau contrôle : 3**, inchangé.
- **23 items relus sur 50**, 27 restants.

### 25. `b06-014` — accord complet, et une imprécision manquée des deux côtés

| | 1 `exactitude_technique` | 2 `absence_de_bugs` | 3 `respect_consignes` | verdict |
|---|---|---|---|---|
| annotateur, premier passage | V | V | V | **PASS** |
| étiquette | V | V | V | **PASS** |

Dix-septième accord consécutif. Les deux réfutations demandées sont exactes — inférence à la compilation,
bytecode identique — et le recentrage sur la lisibilité est pertinent. Aucune correction du corpus.

**Réserve portée contre l'étiquette elle-même.** La réponse affirme que `var` ne s'applique « jamais aux
champs ni aux paramètres ». C'est exact pour les paramètres de méthode, **inexact pour les paramètres de
lambda**, autorisés depuis Java 11 sous la forme `(var x, var y) -> …`. Le `<thinking>` de référence ne
mentionne pas les lambdas — vérifié, aucune occurrence — et l'annotateur ne l'a pas relevé davantage.

L'imprécision est mineure et ne renverse pas le verdict : la question posée portait sur deux arguments
précis, tous deux correctement réfutés. Mais elle est consignée, **parce qu'un accord peut être un accord
sur une inattention commune** — et c'est précisément ce que le κ ne distingue pas d'un accord éclairé.
À verser au REX comme limite de la mesure d'accord inter-annotateur.

### État de la relecture

- **Accord sur le verdict, premier passage : 23 / 24.**
- **Désaccords au niveau contrôle : 3**, inchangé.
- **24 items relus sur 50**, 26 restants.
- **Inattentions communes repérées : 1** (`b06-014`).
