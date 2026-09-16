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
