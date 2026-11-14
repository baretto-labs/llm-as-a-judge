# Pré-enregistrement — critiques en few-shot

Écrit le **2026-10-17**, **avant que la variante ait vu un seul item**.
`results/runs/` ne contient aucun fichier
`14B-baseline-conventions-fewshot.jsonl` au moment où ce document est écrit.

## La question

La méthode de référence du domaine — Hamel Husain, *Using LLM-as-a-Judge For
Evaluation*, « critique shadowing » — tient en une boucle : l'expert tranche en
binaire **et écrit une critique**, et ce sont **les critiques qui deviennent les
exemples few-shot du juge**. Il range explicitement « pas de critiques dans
l'invite » parmi les erreurs d'invite de juge, et note que fine-tuner un juge
est rare.

Cette étude a fait l'inverse. `configs/conventions.md` fait **19 lignes et
quatre règles abstraites, zéro exemple**. Quand les règles n'ont plus suffi, le
levier suivant essayé a été **l'entraînement**, 91 minutes.

Ce que le banc a déjà mesuré (diapositive 21 du support, `results/metrics.json`) :

| | justesse | accord κ | stabilité |
|---|---|---|---|
| invite nue | 0 % | 0,00 | 0 % |
| + 4 conventions | 76 % | **0,48** | 76 % |
| + entraînement | 76 % | **0,44** | 58 % |

Les conventions achètent l'accord. L'entraînement ne l'achète pas. **Et le
levier que la littérature désigne comme principal n'a jamais été essayé.**

**La question posée ici : six critiques en few-shot, à conventions identiques et
sans rien entraîner, améliorent-elles l'accord du juge avec l'étalon ?**

## Le dispositif

**`14B-baseline-conventions-fewshot`**, déclarée dans `configs/variants.json` le
2026-10-17 avec sa paire de comparaison, port 8086 :

| | |
|---|---|
| modèle | `mlx-community/Qwen2.5-Coder-14B-Instruct-4bit` — **le même** que la variante à conventions |
| adaptateur | aucun. **Rien n'est entraîné** |
| suffixe système | `configs/conventions-fewshot.md` = `conventions.md` **mot pour mot** + six exemples |
| items, passes, température | les **mêmes 50**, **3 passes**, T = 0,2 |
| harnais | `scripts/bench_variant.sh`, inchangé |

La variante ne diffère de `14B-baseline-conventions` **que par ce suffixe**.
C'est la seule raison pour laquelle l'écart sera imputable aux exemples.

### Les six exemples, gelés ici

Produits par `scripts/build_fewshot.py` depuis `data/mlx/train.jsonl`, règle de
sélection écrite dans son en-tête et figée avant exécution : pour chacun des six
couples (tâche, verdict), le **premier item `cas == "limite"`** en ordre de
fichier.

```
  b11-009  CODE_ANALYSIS          PASS      b02-009  CODE_ANALYSIS          FAIL
  b12-004  RAG_CONTEXT_RELEVANCE  PASS      b13-006  RAG_CONTEXT_RELEVANCE  FAIL
  b14-020  RAG_FAITHFULNESS       PASS      b14-018  RAG_FAITHFULNESS       FAIL
```

**Des cas limites et non un panachage** : la variante à conventions rend déjà
76 %, c'est-à-dire qu'elle tranche les cas francs. Ce que des critiques peuvent
transmettre, c'est l'arbitrage des cas ambigus — là où κ s'effondre. Aucun ne
sera remplacé après lecture des résultats.

**Cloisonnement** : les six viennent du **train**. `build_fewshot.py` s'arrête
s'il en trouve un dans `data/golden/test.jsonl`. Le contrôle est passé.

## Divergences avec la méthode, déclarées avant

1. **Les critiques ne sont pas écrites par un expert humain.** Le `<thinking>`
   de chaque exemple vient du corpus, dont les étiquettes sont **produites par
   un modèle** (`data/REVUE_GOLDEN.md`, en-tête). La relecture en aveugle a
   porté sur les 50 items du **test**, pas sur le train : **aucune des six
   critiques n'a été relue par qui que ce soit.** C'est une divergence de fond
   avec « critique shadowing », pas une approximation. Elle se dira à l'oral.
2. **Six exemples, pas une boucle d'itération.** Husain décrit trois tours
   d'allers-retours avec l'expert jusqu'à convergence de l'accord. Ici, un seul
   tir. Un résultat négatif ne réfutera donc **pas** la méthode : il dira que
   son premier tour, sans expert, ne suffit pas.
3. **Un juge n'ayant vu que des cas limites peut devenir erratique sur les cas
   francs.** La justesse le révélera, elle couvre les deux. Déclaré ici pour
   qu'un effondrement de la justesse ne soit pas raconté comme une surprise.

## Métrique principale, déclarée avant

**κ de Cohen entre le verdict de la variante few-shot et l'étalon**, sur les
50 items, calculé par `scripts/benchmark_judges.py` sans aucune modification.

Référence de comparaison, déjà publiée : **κ = 0,48, IC95 [0,29 ; 0,66]** pour
`14B-baseline-conventions`.

Lecture **fixée à l'avance** :

| κ few-shot | conclusion |
|---|---|
| **≥ 0,66** | au-delà de la borne haute de l'intervalle des conventions. Les critiques améliorent l'accord : le levier que l'étude n'avait pas essayé est le bon, et il coûte six exemples contre 91 minutes d'entraînement. Va à l'écran. |
| **0,29 – 0,66** | **non concluant**, et c'est le mot qui sera employé — pas l'estimation ponctuelle. Chiffre brut rapporté, aucune affirmation à l'écran au-delà de « essayé, non concluant à n = 50 ». |
| **< 0,29** | les critiques **dégradent** l'accord. Résultat négatif contre la littérature, publié tel quel et sans adoucissement. |

À n = 50, la bande du milieu est l'issue la plus probable. **Elle est acceptée
d'avance**, et le talk peut la raconter : « j'ai essayé le levier que tout le
monde recommande, mon banc ne sait pas trancher à cette taille » est un
enseignement, pas un échec de manipulation.

## Mesures secondaires, déclarées sans pouvoir de décision

1. **Justesse sur les 50 items.** Rapportée, **sans verdict** : à n = 50
   l'étude ne détecte pas en dessous de ~15 points (`PREENREGISTREMENT.md` § 5).
   Sert uniquement au contrôle de la divergence n° 3 ci-dessus — un effondrement
   franc serait visible bien au-delà du seuil de détection.
2. **Stabilité du verdict** sur les 3 passes, à comparer aux 76 % des
   conventions. Descriptif.
3. **Les 8 erreurs systématiques** de la variante à conventions — `b03-005`
   `b03-014` `b04-002` `b04-014` `b06-008` `b07-002` `b09-014` `b12-011`, gelées
   dans `PREENREGISTREMENT_JURY.md` — : combien la variante few-shot en corrige.
   Même régime descriptif que le jury, **jamais en pourcentage** sur n = 8.
   Déclaré ici pour que ce décompte soit comparable aux 3/8 de l'entraînement et
   au résultat Mistral, et non choisi après coup parce qu'il est flatteur.
4. **Longueur de sortie.** La sonde du 2026-10-17 a relevé 339 et 386 jetons de
   complétion contre 237 pour les conventions seules : les exemples allongent le
   raisonnement. Rapporté parce que le support affirme ailleurs que la verbosité
   n'est pas pénalisée, et qu'un juge plus bavard coûte plus cher à faire tourner.

## Coût, mesuré avant de le dépenser

Sonde du 2026-10-17, trois appels sur le port 8086, ajustement à deux points :

```
  conventions seules      930 jetons d'invite   37,9 s   475 jetons rendus
  + few-shot (1er appel) 6831 jetons d'invite   69,6 s   386 jetons rendus
  + few-shot (2e appel)  6878 jetons d'invite   65,7 s   339 jetons rendus

  décodage 12,0 jetons/s · préremplissage fixe 37,4 s · préfixe NON mis en cache
```

Les deux appels few-shot se reconstituent exactement par ce modèle. Le serveur
MLX ne réutilise pas le préfixe d'un appel à l'autre : **les 37 s se paient
150 fois**. Budget attendu : **2 h 25 à 2 h 55** pour 150 générations, contre
53,7 min relevées pour `14B-baseline-conventions`.

## Règle d'arrêt

Les **150 générations**, 50 items × 3 passes, **sans arrêt anticipé et sans
examen intermédiaire des verdicts**. Le κ ne sera calculé qu'une fois les 150
passées.

## Ce qui ne sera pas fait

- **Aucun second jeu d'exemples si le résultat déplaît.** Les six identifiants
  sont gelés ci-dessus. Un autre tirage serait une expérience nouvelle, à
  déclarer avant, et les deux résultats seraient publiés.
- **Aucun ajustement du nombre d'exemples après lecture.** Six, pas trois ni douze.
- **Aucune reformulation du κ publié.** S'il est inférieur à 0,48, il est publié
  tel quel : c'est l'objet même de la mesure.
- **Aucune modification de `configs/conventions.md`.** La comparaison ne tient
  que si les conventions sont identiques mot pour mot dans les deux variantes.

## Ce que le résultat changera dans l'exposé

Quel qu'il soit, il ajoute une ligne au tableau de la diapositive 21 et il
arme le passage REX : *« le levier que la littérature désigne comme principal,
je ne l'avais pas essayé — je l'ai essayé, voilà ce que ça donne. »*

Si le résultat est **non concluant**, c'est cette phrase-là qui est dite, et le
tableau porte « non concluant » et non le chiffre nu.
