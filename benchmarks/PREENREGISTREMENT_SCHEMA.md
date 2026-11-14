# Pré-enregistrement — le juge à sortie structurée

Écrit le **2026-10-18**, **avant que ce juge ait vu un seul item** et **avant que la
moindre ligne de son code soit écrite**. Preuve positive au moment de l'écriture :
`ls benchmarks/rag-campaign-juge-*.jsonl` ne retourne aucun fichier portant l'étiquette
`schema-*`, et `grep -rn "responseFormat" src/` ne retourne rien.

## La question

Les deux juges de la campagne rendent du **texte libre**. Trois expressions régulières en
extraient le verdict (`RagContextJudge:141-143`), et toute sortie inanalysable vaut
`INVALID` — comptée comme désaccord, jamais comme PASS.

Ce que le banc de l'étalon a déjà mesuré, repassé dans le parseur du dépôt :

| variante | INVALID / total |
|---|---|
| `14B-baseline-nu` | **150 / 150 (100 %)** |
| `14B-baseline-conventions` | 0 / 150 |
| `14B-finetuned` | 0 / 150 |
| `32B-baseline-conventions` | 0 / 150 |
| `Mistral-24B-baseline-conventions` | 10 / 150 (6,7 %) |
| `14B-baseline-conventions-fewshot` | 3 / 153 (+ 3 erreurs HTTP) |

L'invite nue **n'est pas un juge qui juge mal** : c'est un juge qui ne rend jamais le
format. Il raisonne, il emploie les bons noms de contrôles, il s'arrête avant le JSON. Et
**rien n'est tronqué** — budget 1024 jetons, plus longue sortie 831.

Le levier derrière le **0 % → 76 %** est donc « écrire le format attendu », pas « écrire
des règles de jugement ». **Un schéma contraint achèterait cette part gratuitement.**

**La question posée ici : à invite identique, contraindre le décodage par un schéma
JSON change-t-il les verdicts du juge ?**

## Pourquoi ce n'était pas déjà fait, et pourquoi la raison inscrite est fausse

`RagContextJudge:40-44` justifie l'appel brut ainsi : la sortie commence par un bloc
`<thinking>`, « la sortie structurée de LangChain4j exige un JSON seul et échouerait ».

Vérifié dans les jars le 2026-10-18 : `OllamaChatRequest` porte `setFormat(Object)` **et**
`setThink(Boolean)` ; le builder expose `.responseFormat(...)`, `.think(true)`,
`.returnThinking(true)`. **Raisonnement et schéma sont orthogonaux.** La contrainte réelle
est celle d'un seul serveur : `mlx_lm.server` 0.31.3 n'implémente pas `response_format`
(aucune occurrence dans `server.py`, aucun décodage sous grammaire) et **ignore le champ en
silence**. Ollama 0.40.6 accepte un schéma complet.

Le commentaire sera corrigé. Il n'est pas supprimé : l'arbitrage était bon pour la voie MLX,
sa justification était trop générale.

## Le dispositif

**Étiquette `schema-coder32b`**, troisième juge de la campagne, déclaré ici avec sa paire.

| | |
|---|---|
| réponses jugées | **les mêmes 180** de `benchmarks/rag-campaign.jsonl` — **aucune régénération** |
| modèle | **`qwen2.5-coder:32b`** — **le même modèle que le juge 1** de cette campagne (`mlx-community/Qwen2.5-Coder-32B-Instruct-4bit`) |
| serveur | **Ollama** 0.40.6 (MLX ne sait pas servir un schéma) |
| raisonnement | `think(true)` — le `<thinking>` part dans le champ natif d'Ollama, **pas dans le JSON** |
| invite système | `SYSTEM_PROMPT` + `judge-finetune/configs/conventions.md`, **mot pour mot inchangés** |
| critères | les mêmes libellés verbatim, **inchangés** |
| température | 0,0, comme les deux autres |
| activation | `-Djmh.judge.schema=true`, **par défaut false** — les classes publiées gardent leur comportement |

Le modèle est **choisi pour isoler le schéma** : c'est celui du juge 1, pas un modèle de plus.
Ce qui l'en sépare, et qui est **confondu avec la contrainte de décodage**, est déclaré ici et
non découvert après coup :

1. **le serveur** — Ollama au lieu de `mlx_lm.server`, puisque MLX ne sait pas servir un schéma ;
2. **la quantification** — Q4_K_M côté Ollama contre 4 bits MLX, deux chemins de quantification
   différents pour les mêmes poids d'origine ;
3. **la contrainte de décodage** elle-même, qui est l'objet de la mesure.

Ces trois-là bougent ensemble et **aucune des trois ne peut être isolée** par ce dispositif. La
métrique principale — le taux d'INVALID — reste interprétable malgré ce confondu, parce qu'elle
porte sur une propriété de **forme** que seul le schéma peut garantir par construction. Les
mesures secondaires, elles, en portent la marque, et c'est pourquoi aucune ne décide de rien.

N'est en revanche **pas** confondu : l'invite, les critères, les conventions, la température et
les 180 réponses jugées sont identiques, mot pour mot, à ceux des deux juges MLX. Et le générateur
(`qwen3.8:27b`) **n'est pas** ce juge — l'auto-jugement est écarté.

### Le schéma, gelé ici

```
juge de contexte           juge de réponse
  checks.contexte_pertinent    checks.affirmations_etayees
  checks.contexte_suffisant    checks.absence_invention
  checks.bruit_maitrise        checks.citations_exactes
  verdict : enum[PASS, FAIL]   verdict : enum[PASS, FAIL]
  reason  : string             reason  : string
```

`checks` **avant** `verdict`, comme dans le corpus : le modèle génère de gauche à droite,
et doit poser les faits avant de trancher. `additionalProperties` interdit. Les trois clés
de `checks` sont **requises**, ce qui rend un contrôle manquant impossible.

**Pas de champ `thinking` dans le schéma** : Ollama le rend à part. Si le serveur ne
rendait pas de `thinking`, ce serait une divergence à déclarer, pas à rattraper en
l'ajoutant au schéma après coup.

## Métrique principale, déclarée avant

**Le taux d'INVALID du juge à schéma, sur les 360 jugements** (180 contextes + 180 réponses).

Lecture **fixée à l'avance** :

| INVALID | conclusion |
|---|---|
| **0** | le schéma tient sa promesse : la classe d'échec disparaît par construction. Va à l'écran. |
| **1 – 5** | le schéma réduit sans supprimer. Rapporté tel quel, aucune affirmation de suppression. |
| **> 5** | le schéma **ne tient pas** sur cette pile. Publié tel quel, et la cause cherchée côté serveur. |

Référence : les deux juges MLX de la même campagne, dont le taux d'INVALID sera connu
**avant** que celui-ci tourne. C'est assumé — la comparaison porte sur une grandeur de
format, pas sur un verdict, et aucune des trois lectures ci-dessus ne dépend de leur valeur.

## Mesures secondaires, déclarées sans pouvoir de décision

1. **Accord des verdicts** entre le juge à schéma et chacun des deux juges MLX (κ de Cohen
   et accord brut, par le `cohen_kappa` unique du dépôt). **Descriptif.** La campagne RAG
   n'a **aucune étiquette de référence** : cet accord mesure de la **concordance, jamais de
   la justesse**. Aucun des trois ne peut y avoir « raison ».
2. **Ordre des trois bras** (`vector`, `vector-bm25`, `graphrag`) selon ce juge. Même
   contrôle que pour le second juge : **ordre identique** ⇒ la contrainte de décodage n'a
   pas porté le résultat ; **ordre divergent** ⇒ **aucun classement ne va à l'écran**.
3. **Longueur de sortie et durée par jugement**, contre les deux juges MLX. Rapporté parce
   qu'un décodage contraint change le coût, et que le support parle de coût.

## Ce qui ne sera pas fait

- **Aucune modification de l'invite, des critères ou des conventions.** La comparaison ne
  tient que s'ils sont identiques mot pour mot dans les trois juges.
- **Aucun second schéma si le premier déplaît.** Il est gelé ci-dessus.
- **Aucun re-jugement des deux juges MLX.** Leurs fichiers sont écrits et ne sont pas
  réécrits.
- **Aucune régénération des 180 réponses.**
- **Aucun classement des trois bras sur la foi de ce juge seul.**

---

## Amendement du 2026-10-18 — `think` retiré, divergence déclarée

Écrit **avant les 180 jugements** : `benchmarks/rag-campaign-juge-schema-coder32b.jsonl`
n'existe pas à cet instant.

Le dispositif gelé plus haut prévoyait `think(true)` pour que le raisonnement parte dans le
champ natif d'Ollama, hors du JSON contraint. **Ce n'est pas possible avec ce modèle** :
Ollama refuse l'appel avec `{"error":"\"qwen2.5-coder:32b\" does not support thinking"}`.
Constaté sur une sonde de 2 items, dont les 4 jugements sont revenus en échec d'appel.

Le pré-enregistrement avait fixé la conduite pour ce cas exact — « si le serveur ne rendait
pas de `thinking`, ce serait une divergence à déclarer, pas à rattraper en l'ajoutant au
schéma après coup ». Elle est appliquée telle quelle :

- `think(true)` et `returnThinking(true)` sont **retirés** de la branche à schéma ;
- **aucun champ `thinking` n'est ajouté au schéma**, qui reste celui gelé plus haut ;
- le modèle reste `qwen2.5-coder:32b`, celui du juge 1, pour ne pas ajouter un confondu.

### Ce que cette divergence coûte, dit avant les résultats

Le juge à schéma **ne raisonne pas avant de trancher**. Les deux juges MLX, eux, produisent
un bloc `<thinking>` en texte libre parce que `SYSTEM_PROMPT` le leur demande ; sous schéma
contraint, ce bloc est structurellement impossible — le décodage ne peut émettre que le JSON.

**Un quatrième confondu s'ajoute donc aux trois déjà déclarés : l'absence de raisonnement.**
Il est de loin le plus lourd, et il va dans le sens *défavorable* au juge à schéma. Lecture
qui en découle, fixée ici :

- la **métrique principale** (taux d'INVALID) reste interprétable : elle porte sur la forme,
  que seul le schéma garantit par construction, et l'absence de raisonnement ne peut pas la
  flatter ;
- **toute comparaison de verdicts** avec les juges MLX — κ, ordonnancement des bras — devient
  encore moins décisoire qu'annoncé. Un désaccord ne dira pas « le schéma change les verdicts »
  mais « schéma sans raisonnement contre raisonnement sans schéma », ce qui ne se démêle pas.
  Aucun chiffre d'accord ne va à l'écran à partir de ce dispositif.

### Sonde, déclarée parce qu'elle a montré des verdicts

La sonde de vérification a porté sur les **2 premières lignes** de `rag-campaign.jsonl`
(bras `vector`), soit 4 jugements, et ses verdicts ont été vus : `ctx=PASS rep=FAIL` et
`ctx=FAIL rep=PASS`. Elle servait à vérifier que le schéma tient avant de dépenser 360
jugements. Elle n'a **rien modifié** au dispositif au-delà du retrait de `think` ci-dessus,
et ses 2 items seront rejugés avec les 178 autres, sans traitement particulier.

### Ce qui reste interdit

- Ajouter un champ `thinking` au schéma, maintenant ou après lecture des résultats.
- Changer de modèle pour en prendre un qui accepte `think` : ce serait une **expérience
  nouvelle**, à déclarer avant, et les deux résultats seraient publiés.

---

## Amendement du 2026-10-19 — le plafond de 512 jetons, et ce qu'il peut expliquer

Écrit **avant les deux relances** décrites ici :
`benchmarks/diagnostic/rag-campaign-juge-32B-budget2048.jsonl` n'existe pas, et
`benchmarks/rag-campaign-juge-gemma-4-26b-a4b.jsonl` est le fichier en panne décrit plus bas,
mis de côté hors de `benchmarks/` avant toute relance.

### Le constat

`mlx_lm.server` plafonne la génération à **512 jetons** par défaut (`--max-tokens`, défaut 512
dans `server.py:1842-1845`). Ni `RagContextJudge` ni `RagAnswerJudge` ne fixent de budget : les
deux juges MLX ont donc tourné à 512, et ce n'était écrit nulle part.

**Conséquence constatée sur gemma-4-26b-a4b** : ce modèle raisonne dans le champ `reasoning`
de la réponse OpenAI et n'émet `content` qu'après. À 512 jetons il n'y arrive jamais —
`content: None`, `finish_reason: length`, HTTP 200. Résultat : **326 INVALID sur 338 jugements**,
sans un seul message d'erreur. Sonde directe du 2026-10-19 : à 80 jetons `content=None` ; à
3 000 jetons, `{"verdict":"PASS"}` rendu en 112 jetons au total. **Le run gemma est une panne de
harnais, pas une mesure** : ses 180 lignes sont écartées, et l'accord ainsi que l'ordonnancement
qui l'impliquaient ne valent rien (11 verdicts de contexte exploitables sur 180).

### Ce que ça met en doute, et qui n'est pas gemma

Le juge MLX Qwen2.5-Coder-32B a rendu **37 INVALID sur 360**, tous avec le motif
`"Aucun verdict analysable"`. **Le texte brut n'est pas conservé**, donc rien dans les données
ne permet de distinguer :

- **(A) le modèle n'écrit pas le format attendu** — la lecture jusqu'ici ;
- **(B) le modèle a été coupé à 512 jetons** avant d'arriver au JSON, son `<thinking>` ayant
  consommé le budget.

Les deux sont de vrais avantages de la sortie structurée — elle n'a pas de raisonnement à
financer — mais **ce ne sont pas la même affirmation**, et le talk ne peut pas choisir la plus
flatteuse sans l'avoir mesurée.

### Relance 1 — diagnostic de troncature, lecture fixée avant

Les **37 items** dont au moins un verdict valait INVALID chez le juge MLX 32B sont rejugés
**par le même modèle, même invite, mêmes conventions, température identique**, avec
`MAX_TOKENS=2048` au lieu de 512. Étiquette **`32B-budget2048`**, dans
`benchmarks/diagnostic/`, hors du répertoire que lit `rapport_campagne.py`.

C'est un **diagnostic de harnais, pas une variante de juge** : il ne remplace aucun verdict
publié, n'entre dans aucune comparaison de bras, et aucun de ses verdicts PASS/FAIL ne sera
reporté dans le tableau des stratégies.

| redeviennent analysables | conclusion, écrite maintenant |
|---|---|
| **≥ 28 des 37** (3/4) | l'écart 0 ↔ 37 est **d'abord un effet de budget**. La phrase à l'écran devient « le schéma n'a pas de raisonnement à financer : il tient dans le budget », pas « le schéma discipline le format ». |
| **9 à 27** | les deux causes coexistent. **Aucune des deux phrases ne va à l'écran** : le chiffre brut est donné avec la cause déclarée indéterminée. |
| **≤ 8** (1/4) | la troncature n'explique pas l'essentiel : c'est bien le **format** que le schéma achète, et la lecture initiale tient. |

### Relance 2 — gemma rejoué, et ce qu'il ne pourra pas servir

Même modèle, même invite, `MAX_TOKENS=4096`. Étiquette **`gemma-4-26b-a4b`**, le fichier en
panne étant déplacé hors de `benchmarks/` au préalable.

**Différence déclarée** : gemma tournera à 4096 là où le juge MLX 32B a tourné à 512. Ce n'est
plus le même harnais. Conséquence fixée ici :

- gemma sert **au seul contrôle d'ordonnancement des bras** — un classement est robuste au
  budget dès lors que les INVALID sont rares ;
- **aucun κ impliquant gemma ne va à l'écran**, et aucun de ses taux de PASS n'est comparé à
  ceux des deux autres juges ;
- si gemma rend encore **plus de 18 INVALID sur 360** (5 %), son run est déclaré inexploitable
  une seconde fois et **le contrôle d'ordonnancement restera à deux juges**, ce qui sera dit tel
  quel à l'oral.

### Ce qui ne sera pas fait

- **Aucune relance du juge MLX 32B sur les 180 items** à budget élargi : ce serait une variante
  nouvelle, à déclarer avant, et elle rendrait les 37 INVALID publiés incomparables aux leurs.
- **Aucun verdict publié n'est réécrit** par ces deux relances.
- **Aucun ajustement du seuil de 28/9 ci-dessus après lecture.**
