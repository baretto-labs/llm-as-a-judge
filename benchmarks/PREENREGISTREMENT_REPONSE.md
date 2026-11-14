# Pré-enregistrement — évaluation de la réponse, trois bras de récupération

Écrit le **2026-10-17**, **avant la moindre génération**. Preuve positive à cet instant :
`benchmarks/rag-quality-detail.jsonl` ne contient que des lignes `"schema":"binaire-v1"`,
toutes horodatées du 2026-09-24, et aucune ligne portant un champ `answer`.

## Pourquoi cette campagne

Deux défauts du dispositif actuel, l'un de fond, l'autre de protocole.

**1. On n'évaluait pas la réponse.** Le banc ne jugeait que le contexte récupéré. Aucune
réponse n'était générée nulle part dans le dépôt — `RetrievalBenchmark` ne contient aucun
appel de modèle de chat. Le champ `generated` du détail contenait en réalité **les extraits
Java retournés par le moteur**, ce qui a déjà induit une lecture fausse du support. L'exposé
affirme qu'on évalue aussi la réponse ; cette campagne rend l'affirmation vraie.

**2. La campagne du 2026-09-24 a été jugée par la pire variante disponible.** Son juge était
`Qwen2.5-Coder-14B + adapters/14b-judge-ckpt200`, c'est-à-dire le juge *fine-tuné* — celui
que le banc de `judge-finetune/` a mesuré **en dessous** des simples conventions :

| | justesse | accord κ | stabilité |
|---|---|---|---|
| invite nue | 0 % | 0,00 | 0 % |
| + 4 conventions | 76 % | **0,48** | 76 % |
| + entraînement *(le juge du 2026-09-24)* | 76 % | **0,44** | 58 % |

Ce n'est pas un ajustement de confort : c'est une correction.

## Le dispositif

| | |
|---|---|
| source | OllamAssist, `src/main/java` (code réel, jamais le corpus synthétique) |
| questions | les 60 de `QuestionCorpus`, identiques pour tous les bras |
| génération | **Ollama `llama3.1:latest`**, T = 0, invite de production `RagService.buildPrompt` |
| juge de contexte | **MLX `Qwen2.5-Coder-32B-Instruct-4bit`**, T = 0, `RAG_CONTEXT_RELEVANCE`, + conventions, **aucun adaptateur** |
| juge de réponse | **le même serveur**, `RAG_FAITHFULNESS`, + conventions |
| schéma de sortie | `binaire-v2` — `generated` devient `context`, les champs `answer*` apparaissent |

**Le générateur et le juge ne sont pas de la même famille, et c'est une condition de
validité, pas un réglage.** Un modèle qui note sa propre sortie la surévalue — biais
d'auto-préférence. Juge Qwen, générateur Llama (voir l'amendement du 2026-10-17 ci-dessous :
c'est le générateur qui a changé de famille, pas le juge).

**Le juge de réponse reçoit le contexte exact soumis au générateur**, pas la liste brute :
sinon il sanctionnerait comme invention une phrase tirée d'un extrait qu'il n'aurait pas vu.

## Les trois bras, déclarés ici

| bras | préréglage | moteur |
|---|---|---|
| **vectoriel** | `knn-only` | Lucene — kNN seul, k = 5, ni BM25 ni RRF |
| **vectoriel + BM25** | `hybrid` | Lucene — BM25 + vecteur, fusionnés par RRF, k = 10 |
| **graphrag** | `hybrid-graph` | Neo4j — hybride + expansion de graphe à 1 saut |

Deux exécutions suffisent, le banc étant apparié Lucene ↔ Neo4j :

```
  -Drag.scenario=knn-only|hybrid-graph     → vectoriel        + graphrag
  -Drag.scenario=hybrid|hybrid-graph       → vectoriel + BM25 + graphrag
```

**Le bras graphrag est donc mesuré deux fois, sur les mêmes 60 questions.** Déclaré ici pour
qu'on ne puisse pas, après coup, présenter les deux mesures comme 120 observations : ce sont
60 questions mesurées deux fois. L'écart entre les deux mesures sera publié tel quel — c'est
une mesure gratuite de la **stabilité du juge**, et rien d'autre.

## Paires de comparaison, déclarées avant

| | a | b | ce que ça teste |
|---|---|---|---|
| **principale** | vectoriel | vectoriel + BM25 | ce que BM25 achète, à moteur et questions identiques. C'est le chiffre que la diapo 12 affirme sans l'avoir dans le dépôt. |
| secondaire 1 | vectoriel + BM25 | graphrag | réplication de la comparaison du 2026-09-24, avec un juge corrigé |
| secondaire 2 | verdict contexte | verdict réponse | sur un même item : combien de fois un contexte jugé insuffisant produit quand même une réponse **fidèle** (le modèle se tait proprement) contre **infidèle** (il brode) |

Toute autre paire lue après coup sera signalée comme exploratoire.

## Lecture fixée à l'avance

**Métrique principale** : taux de PASS du **contexte**, test de McNemar apparié sur les
60 questions, pour la paire principale.

À n = 60, l'étude ne détecte pas en dessous d'une quinzaine de points. Trois issues,
écrites maintenant :

| | conclusion |
|---|---|
| p < 0,05 **et** ≥ 15 points d'écart | BM25 change quelque chose ; le chiffre va à l'écran |
| p ≥ 0,05 | **non concluant**, et c'est le mot employé — pas l'estimation ponctuelle |
| écart < 15 points, quel que soit p | rapporté brut, aucune affirmation à l'écran |

**La secondaire 2 n'a pas de seuil** : c'est un décompte, publié en effectifs et jamais en
pourcentage. C'est elle qui porte la démonstration de la thèse du talk.

## Amendement du 2026-10-17, avant toute génération

**Preuve positive à l'instant où il est écrit** : `benchmarks/rag-quality-detail.jsonl`
contient 240 lignes, **0** portant `"schema":"binaire-v2"` et **0** portant un champ
`answer`. Aucun résultat de cette campagne n'existe.

**Ce qui change** : le juge passe de `Mistral-Small-3.2-24B-4bit` (port 8085) à
`Qwen2.5-Coder-32B-Instruct-4bit` (port 8083), et le générateur de `qwen2.5:7b` à
`llama3.1:latest`.

**Pourquoi.** La première version de ce document choisissait le juge sur un argument —
famille disjointe du générateur — sans le confronter à une mesure. Le banc
`judge-finetune` a rendu ses chiffres dans la nuit, sur les 50 items de l'étalon :

| juge candidat | κ avec l'étalon | justesse | stabilité | fidélité RAG |
|---|---|---|---|---|
| `Mistral-24B` + conventions | 0,349 | 64 % | 78 % | — |
| `Qwen2.5-Coder-32B` + conventions | **0,801** | **90 %** | **92 %** | **0,97** |

La colonne de droite est la justesse moyenne sur `affirmations_etayees`,
`absence_invention`, `citations_exactes` — exactement les trois contrôles que le juge de
réponse applique. Le biais d'auto-préférence est un **risque** ; un juge qui s'accorde deux
fois moins avec l'étalon est un **défaut déjà constaté**. On garde les deux arguments en
déplaçant la contrainte : le juge se choisit sur son accord mesuré, le générateur est une
constante identique sur les trois bras et n'a donc qu'à satisfaire la disjonction.
`llama3.1:latest` la satisfait, pèse 4,9 Go et est déjà en cache.

**Reste à vérifier avant de lancer** : 18,4 Go (juge) + ~5 Go (générateur) résidents contre
la limite *wired* de ~27 Go qui a déjà provoqué un OOM Metal le 2026-10-17. À mesurer, pas à
supposer — la sonde de coût ci-dessous relèvera aussi la mémoire de pointe.

## Ce qui ne sera pas fait

- **Aucune comparaison avec les chiffres du 2026-09-24.** Le juge a changé de modèle, perdu
  son adaptateur et gagné les conventions. Les deux campagnes ne sont pas commensurables, et
  les présenter côte à côte serait une faute. L'ancienne campagne reste publiée telle quelle.
- **Aucun arrêt anticipé, aucun examen intermédiaire des verdicts.**
- **Aucun quatrième bras ajouté après lecture.** `hybrid-graph-hyde` et `full` existent dans
  `FeatureFlags` et ne sont pas de cette campagne.
- **Aucun changement de modèle en cours de campagne.**

## Coût — à mesurer avant de le dépenser, pas à estimer

**Non mesuré au moment où ce document est écrit** : le GPU sert le banc few-shot jusque vers
23 h 30, et une variante est servie à la fois.

Volume engagé : 60 questions × 2 exécutions × 2 moteurs = **240 réponses générées**,
240 jugements de contexte et 240 jugements de réponse, soit **720 appels**.

**Avant de lancer la campagne, sonder trois appels de chaque sorte et ajuster à deux points**,
comme le 2026-10-17 pour le few-shot — où la sonde avait révélé que les 37 s de
préremplissage se paient à chaque appel, faisant passer le budget de 54 min à 2 h 30. Un
budget estimé sans sonde n'a aucune valeur ici.

## Ce que le résultat changera dans l'exposé

- La diapo 12 obtient ses chiffres BM25, ou se reformule.
- La diapo 11 gagne un décompte mesuré : combien de fois un contexte insuffisant a produit
  une réponse inventée. C'est la démonstration de la thèse d'ouverture.
- **Le talk ne dépend d'aucun de ces résultats.** L'exemple travaillé `ContextRetriever`
  tient la diapo 11 sans eux. Cette campagne est pour l'article et pour la solidité.

## Amendement du 2026-10-18, avant toute génération

**Preuve positive à l'instant où il est écrit** : `benchmarks/rag-quality-detail.jsonl` contient
240 lignes, **0** portant `"schema":"binaire-v2"`. Aucun fichier `benchmarks/rag-campaign*`
n'existe (`ls` échoue sur « no matches found »). La campagne décrite ci-dessus **n'a jamais été
lancée** : ce document est amendé, pas réécrit après résultats.

### 1. La boucle est coupée en deux, et les bras deviennent indépendants

`RagQualityEvaluation` générait et jugeait dans la même itération, pour deux bras appariés
Lucene ↔ Neo4j. Deux classes la remplacent pour cette campagne :

| | rôle |
|---|---|
| `RagCampaignGenerate` | récupère et génère les 3 bras × 60 questions, écrit `benchmarks/rag-campaign.jsonl`. **Aucun juge appelé.** Refuse d'écraser un fichier existant. |
| `RagCampaignJudge` | relit ce fichier, juge contexte et réponse, écrit `…-juge-<étiquette>.jsonl`. **Aucune génération.** Se relance par juge. |

**Pourquoi.** Le générateur pèse 18 Go et le juge 32B 18,4 Go : ils ne tiennent pas résidents
ensemble sous les ~27 Go utilisables. Et un second juge ne doit pas re-générer 180 réponses.

**Ce que cela change dans le protocole, déclaré ici** : les trois bras sont désormais mesurés en
**une seule exécution**, chacun avec son propre index. Le graphrag n'est donc **plus mesuré deux
fois** ; le § « Les trois bras » ci-dessus décrivait deux exécutions appariées, c'est caduc. La
mesure gratuite de stabilité du juge qu'il offrait est remplacée par le second juge du point 3,
qui mesure la même chose en mieux : un désaccord entre deux modèles plutôt qu'entre deux tirages
du même.

**180 générations** (3 × 60), **360 jugements par juge** (contexte + réponse).

### 2. Le générateur passe à `qwen3.8:27b`, et la disjonction de famille est abandonnée

| | avant | après |
|---|---|---|
| générateur | `llama3.1:latest`, 4,9 Go | **`qwen3.8:27b`, 18 Go**, raisonnement actif |

**La disjonction de famille n'est plus satisfaite et ne sera pas prétendue.** Le premier juge est
`Qwen2.5-Coder-32B` : même famille que le générateur, génération et entraînement différents. Le
§ « Le dispositif » ci-dessus affirme « le générateur et le juge ne sont pas de la même famille,
et c'est une condition de validité » — **cette phrase ne vaut plus**, et c'est la raison d'être
du point 3.

Le choix est assumé : `llama3.1` à 4,9 Go ne ressemble pas à ce qu'un produit sert aujourd'hui,
et faire juger trois stratégies de récupération sur les réponses d'un générateur faible mesure
surtout le générateur. L'alternative — garder un générateur disjoint mais faible — a été écartée
explicitement, pas oubliée.

### 3. Deux juges sur les trois bras, et ce que leur accord mesure

| étiquette | modèle | pourquoi |
|---|---|---|
| `32B-conventions` | `Qwen2.5-Coder-32B-Instruct-4bit` + conventions | κ = 0,801 avec l'étalon, le meilleur juge mesuré |
| `gemma-4-26b-a4b` | `gemma-4-26b-a4b` + conventions | **famille disjointe du générateur**, contrôle du point 2 |

**Déclaré avant de lancer : l'accord entre ces deux juges n'est pas une mesure de justesse.** Les
réponses de la campagne RAG n'ont **aucune étiquette de référence**. Le seul endroit du dépôt où
un juge peut être dit faux est l'étalon `judge-finetune/data/golden/test.jsonl`, 50 items relus.
Ici, un désaccord dit que les deux juges divergent — jamais lequel a raison. Toute phrase du
support qui lirait cet accord comme une justesse sera fausse.

**Lecture fixée d'avance du contrôle** :

| | conclusion |
|---|---|
| les deux juges classent les trois bras dans le **même ordre** | la parenté de famille du point 2 n'a pas porté le résultat ; le classement va à l'écran |
| les deux juges **divergent sur l'ordre** | aucun classement à l'écran. Le désaccord est publié tel quel, et c'est lui qui est raconté |

Aucun troisième juge ne sera ajouté pour départager : il n'y a pas de référence à départager
contre, et en ajouter un reviendrait à choisir le juge sur le résultat qu'il rend.

### 4. Ce qui ne change pas

Les 60 questions, les trois préréglages, la paire principale (vectoriel ↔ vectoriel + BM25), le
seuil de 15 points, les trois issues écrites, et l'interdiction de comparer aux chiffres du
2026-09-24. Rien de ce qui porte un verdict n'est touché par cet amendement.
