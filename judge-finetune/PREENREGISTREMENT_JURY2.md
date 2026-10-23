# Pré-enregistrement — jury de trois familles, une voix chacune

Écrit le **2026-10-20 à 19 h 36**, **avant que Gemma ait vu un seul item**.
Preuve positive à l'instant de l'écriture : `results/runs/` contient six fichiers,
**aucun ne porte « gemma »**.

## C'est une seconde tentative, et elle est déclarée comme telle

`PREENREGISTREMENT_JURY.md` du 2026-10-17 a posé une question et reçu sa réponse :
**2 sur 8**, bande ≤ 3/8, conclusion écrite d'avance — « le jury ne fait pas mieux
qu'un entraînement de plus ». Cette conclusion **n'est pas rouverte**. Le présent
document ne rejoue pas le même banc avec d'autres modèles en espérant un meilleur
tirage : il pose une **question différente**, sur une **autre population** et avec une
**autre métrique**.

| | JURY (17/10) | JURY2 (20/10) |
|---|---|---|
| population | **8 items**, les erreurs systématiques du juge | **les 50 items** de l'étalon |
| métrique | combien des 8 sont corrigées | **justesse du vote majoritaire** |
| comparateur | 3/8, ce que fait un entraînement de plus | **45/50, le meilleur juge seul** |
| votants | 1 modèle disjoint contre le juge | **3 familles, une voix chacune** |

### Ce qui motive JURY2, et qui n'est pas une preuve

Le 2026-10-20, **après** le résultat de JURY, un recomptage sur les données déjà en
banque a montré deux choses :

1. sur l'étalon (27 FAIL / 23 PASS, donc équilibré), les erreurs des cinq
   configurations se répartissent en **55 indulgentes contre 5 sévères** ;
2. un vote majoritaire de ces cinq configurations rend **38/50**, contre **45/50**
   pour le meilleur juge seul, et **ses 12 erreurs sont toutes indulgentes**.

Ces deux chiffres sont **post hoc** et n'iront pas à l'écran en l'état. Ils ont deux
défauts que ce banc corrige : le vote est **déséquilibré** (quatre configurations Qwen
pour une Mistral — ce n'est pas un jury de familles, c'est un Qwen avec un invité), et
aucune lecture n'avait été déclarée. **Le présent document déclare la lecture avant la
mesure. C'est elle, et elle seule, qui pourra faire de cette observation un résultat.**

## Le dispositif

Trois votants, **une famille chacun**, aucun ancêtre de pré-entraînement commun :

| voix | famille | modèle | état |
|---|---|---|---|
| 1 | Qwen | `mlx-community/Qwen2.5-Coder-32B-Instruct-4bit` | **en banque** (2026-10-17) |
| 2 | Mistral | `mlx-community/Mistral-Small-3.2-24B-Instruct-2506-4bit` | **en banque** (2026-10-17) |
| 3 | Google | `mlx-community/gemma-4-31b-it-4bit` | **à générer** |

Les deux premières voix sont **réutilisées telles quelles**, sans régénération : mêmes
50 items, 3 passes, T = 0,2, `max-tokens` 1024, `configs/conventions.md` **mot pour
mot identique**, `scripts/bench_variant.sh` inchangé. La troisième tourne sous
**exactement les mêmes réglages**, port 8087. Aucun adaptateur nulle part : rien n'est
entraîné, ce sont trois invites à conventions.

**Règle de vote, fixée ici :** majorité simple des trois verdicts de variante, chaque
variante ayant d'abord agrégé ses 3 passes par vote majoritaire — c'est la règle
qu'applique déjà `benchmark_judges.py`, pas une seconde logique. Trois votants
impairs : aucune égalité n'est possible, aucune règle de départage n'est nécessaire.

### Pourquoi Gemma-4-31B, alors que Gemma a échoué deux fois

Les deux échecs portent sur `gemma-4-26b-a4b-it-4bit` (38 INVALID sur 238 à 4096
jetons). C'est un **modèle différent** — MoE 26b-a4b contre dense 31b. L'objection
historique contre la famille (« Gemma traite le rôle `system` autrement ») a été
vérifiée aujourd'hui sur le gabarit de ce modèle : `chat_template.jinja` traite
explicitement `['system', 'developer']`. Portail d'intégrité franchi avant d'écrire :
**4 `.safetensors`, 17 Go, 0 blob incomplet.**

Rien de tout cela ne garantit le format. D'où la sonde.

## Sonde, avant de dépenser l'heure

**3 items**, 1 passe, avant le banc complet. Seuil d'abandon déclaré :

- **3/3 verdicts extractibles** par `extract_judgment` du harnais ⇒ le banc est lancé.
- **≤ 2/3** ⇒ **le banc n'est pas lancé**, Gemma est écarté, et JURY2 **meurt ici** :
  on ne cherchera pas une quatrième famille pour la remplacer. Le constat publiable
  devient alors « trois familles essayées, deux seulement savent rendre le format ».

## Garde-fou sur le banc complet

**> 15 verdicts non extractibles sur 150** (10 %) ⇒ la variante est annulée et
**n'est pas lue**. Les deux voix en banque ne sont pas touchées, et JURY2 ne rend rien.

## Les questions, et leur lecture, fixées d'avance

### Q1 — principale : le jury bat-il le meilleur juge seul ?

Justesse du vote à trois familles sur les 50 items, contre **45/50 (90 %)** pour
`32B-baseline-conventions`. Test : **McNemar exact apparié** sur les 50 items, α = 0,05.

- **Jury > 45 et p < 0,05** ⇒ le jury gagne. La diapositive 29 est réécrite dans
  l'autre sens, et le chiffre va à l'écran.
- **Jury ≤ 45** ⇒ **l'ajout de votants n'aide pas**, le chiffre va à l'écran tel quel,
  quelle que soit la valeur de p. C'est le résultat que la simulation post hoc rend le
  plus probable, et il est **accepté d'avance**.
- **Jury > 45 et p ≥ 0,05** ⇒ « non concluant ». C'est le mot qui va à l'écran, pas
  l'estimation ponctuelle. À n = 50, cette bande est probable et elle est acceptée.

### Q2 — l'indulgence est-elle une propriété de la famille ?

Sens des erreurs de Gemma sur les 50 items : **indulgentes** (étalon FAIL, juge PASS)
contre **sévères** (étalon PASS, juge FAIL). Test binomial exact bilatéral.

- **Majorité indulgente, p < 0,05** ⇒ **trois familles sans ancêtre commun, le même
  biais**. La phrase va à l'écran.
- **Majorité indulgente, p ≥ 0,05** ⇒ le sens est rapporté brut, sans la phrase.
- **Majorité sévère** ⇒ l'observation du 20/10 ne généralise pas. Ce résultat va à
  l'écran **aussi**, et il affaiblit la leçon n° 5. Déclaré ici pour qu'il ne puisse
  pas être tu.

### Q3 — descriptive : le sens des erreurs du jury

Répartition indulgentes / sévères des erreurs du vote à trois familles. Aucun seuil,
aucun test : on rapporte la valeur. Sert à dire *comment* le jury se trompe, pas s'il
est bon.

## Confondus, nommés avant la mesure

- **Les trois votants ne sont pas appariés en taille** (32B, 24B, 31B). Un écart de
  justesse entre eux mélange famille et taille. Q1 ne compare pas les votants entre
  eux, elle compare le **vote** au meilleur d'entre eux : ce confondu n'atteint pas Q1,
  mais il interdit toute phrase du type « Mistral est moins bon que Qwen ».
- **n = 50.** La bande « non concluant » est la plus probable pour Q1, et elle est
  acceptée d'avance.
- **L'étalon est écrit par un seul relecteur.** Toute justesse mesurée ici est un
  accord avec ce relecteur, jamais une vérité.

## Ce qui ne sera pas fait

Aucune quatrième famille. Aucune autre règle de vote. Aucun autre comparateur que
45/50. Aucune relance en cas de résultat défavorable. Toute régularité repérée après
coup est post hoc, et n'ira pas à l'écran sans un nouveau pré-enregistrement.

---

# Amendement — 2026-10-20, 20 h 48 : le plafond de sortie passe à 2048 pour Gemma

**Écrit avant la relance, et avant qu'un seul verdict de Gemma ait été lu.** Aucun
dépouillement n'a été exécuté : `scripts/rapport_jury2.py` n'a jamais tourné sur un run
Gemma complet.

## Ce qui a été observé, et qui force la divergence

Le banc a tourné **37 générations** sous `max-tokens 1024` avant d'être arrêté. Le run
partiel est **archivé, pas effacé** :
`results/invalide-20261020-gemma-plafond-1024/Gemma-4-31B-baseline-conventions.jsonl`.

| | |
|---|---|
| générations exploitables | 36 (1 erreur réseau) |
| médiane de sortie | **857 jetons** |
| **sorties au plafond 1024** | **9 sur 36 = 25 %** |
| verdicts non extractibles | **8 sur 36** |
| dont au plafond | **8 sur 8** |
| projection sur 150 | **33 non extractibles**, garde-fou déclaré à 15 |

**Les huit échecs sont exactement les huit sorties coupées.** Aucun échec de format
ailleurs.

## Pourquoi monter le plafond ne casse pas la comparabilité — il la rétablit

Mesuré sur les runs en banque, même plafond de 1024 :

| voix | max jetons | médiane | sorties au plafond |
|---|---|---|---|
| Qwen2.5-Coder-32B | 818 | 415 | **0 / 150** |
| Mistral-Small-24B | 429 | 238 | **0 / 150** |
| Gemma-4-31B | 1024 *(censuré)* | 857 | **9 / 36** |

**Le plafond de 1024 n'a jamais été actif pour les deux voix en banque.** Elles n'en
approchent pas à 200 jetons près. Il n'est contraignant que pour la troisième.

Garder 1024 ne maintiendrait donc pas trois votants « à réglages identiques » : cela
appliquerait à un seul des trois une contrainte que les deux autres n'ont jamais
rencontrée, et ferait porter à la famille Gemma une annulation causée par le harnais.
Le banc mesurerait sa **verbosité**, pas son **jugement** — ce que le présent dossier
reproche par ailleurs au plafond de 6000 caractères du banc RAG (voir
`benchmarks/PREENREGISTREMENT_PLAFOND.md` du même jour).

## Ce qui change, et ce qui ne change pas

- **Change** : `--max-tokens 2048` pour `Gemma-4-31B-baseline-conventions` **seule**.
  Valeur choisie pour reprendre celle du diagnostic de budget du 2026-10-19
  (512 → 2048, 35/37 récupérés), et non ajustée sur les données de Gemma.
- **Ne change pas** : les 50 items, les 3 passes, T = 0,2, `configs/conventions.md`
  mot pour mot, `scripts/bench_variant.sh`, la règle de vote, le garde-fou des
  **15 non extractibles sur 150**, et les trois lectures Q1 / Q2 / Q3. **Aucune
  lecture n'est rouverte.**
- **Les 37 générations à 1024 sont écartées**, pas réutilisées : le banc repart de zéro
  pour cette variante.

## Contrôle ajouté par cet amendement

Le rapport doit afficher le **nombre de sorties atteignant 2048**. S'il est **> 0**, la
même objection renaît et la variante est **annulée** au même titre qu'avec le garde-fou
des non extractibles — on ne montera pas le plafond une seconde fois. Déclaré ici pour
que la troisième tentative ne soit pas possible.

---

# Résultat — 2026-10-21

**Garde-fous passés.** Gemma-4-31B : **0 verdict non extractible sur 150**, **0 sortie au
plafond de 2048**. Les 8 verdicts perdus la veille venaient donc bien du plafond de 1024 du
harnais, pas du modèle. Mistral : 10/150 non extractibles, sous le seuil de 15, conforme aux
6,7 % publiés. Étalon : 50 items, 27 FAIL / 23 PASS.

## Q1 — principale : le jury bat-il le meilleur juge seul ?

| | justesse |
|---|---|
| jury des 3 familles (vote majoritaire) | **47/50 = 94 %** |
| `32B-baseline-conventions` seul | **45/50 = 90 %** |

Discordantes : **2 en faveur du jury, 0 en faveur du juge seul**. McNemar exact
**p = 0,5000**.

**Lecture déclarée appliquée : NON CONCLUANT.** C'est le mot qui va à l'écran, pas
l'estimation. Le jury ne démontre pas qu'il bat le meilleur juge seul — à n = 50, deux
items d'écart ne tranchent rien.

## Q2 — une troisième famille partage-t-elle l'indulgence ?

| famille | indulgent | sévère | p binomial |
|---|---|---|---|
| Qwen2.5-Coder-32B | 4 | 1 | 0,3750 |
| Mistral-24B | 15 | 0 | 0,0001 |
| **Gemma-4-31B** | **1** | **0** | **1,0000** |

**Lecture déclarée appliquée : sens rapporté brut, SANS la phrase** (p ≥ 0,05 pour Gemma).
La généralisation de l'indulgence à une troisième famille **n'est pas acquise** : Gemma ne
commet qu'une seule erreur, il n'y a rien à conclure sur sa direction. Le constat
d'indulgence reste porté par les configurations déjà en banque (55 contre 5), il ne gagne
pas de confirmation indépendante ici.

## Q3 — sens des erreurs du jury (descriptif)

3 erreurs, **3 indulgentes, 0 sévère**.

## Brut, noté, NON PRÉSENTABLE : Gemma seul rend 49/50

| juge seul | justesse |
|---|---|
| Gemma-4-31B | **49/50** |
| Qwen2.5-Coder-32B | 45/50 |
| Mistral-24B | 35/50 |

Discordantes Gemma/Qwen : **4–0**, McNemar exact **p = 0,1250**. Accord entre les deux :
46/50. L'unique erreur de Gemma, `b06-008`, est **aussi** une erreur de Qwen.

**Pourquoi ce chiffre ne va pas à l'écran** : la justesse comparée des juges n'est pas une
question déclarée de ce banc — Q1 oppose le *jury* au 32B, pas Gemma au 32B. Et la règle
tient depuis `PREENREGISTREMENT.md` § 5 : à n = 50 l'étude ne détecte pas en dessous de
~15 points, et **aucune règle d'arbitrage entre familles ou tailles n'est inventée après
coup**. 8 points d'écart, p = 0,1250 : c'est exactement la zone que le dispositif ne tranche
pas. Le chiffre est consigné ici ; l'exploiter demande un nouveau pré-enregistrement.

## Ce que le banc change dans l'exposé

1. **La diapositive 29 ne gagne pas son chiffre.** Le jury reste une piste non démontrée :
   94 % contre 90 %, p = 0,5000. Deuxième tentative, deuxième non concluant — et cette fois
   sur la bonne population (50 items) avec la bonne métrique (justesse du vote).
2. **Le vote majoritaire n'a pas rattrapé le meilleur juré, il l'a tiré vers le bas** : le
   jury rend 47/50 là où son meilleur membre en rend 49/50. Voter avec un juré à 35/50 coûte
   des items. Observation post hoc, non présentable comme résultat.
3. **L'incident de la veille est tranché** : à budget suffisant, la famille qu'on a failli
   annuler est la plus juste des trois. La limite était la nôtre.
