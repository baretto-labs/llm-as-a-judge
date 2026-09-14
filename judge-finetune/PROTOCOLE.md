# Protocole — juge LLM fine-tuné (Qwen2.5-Coder 14B vs 32B)

> **Objectif unique : exactitude, rigueur et fiabilité du juge.** Aucune rétrocompatibilité n'est
> maintenue avec les anciens dispositifs d'évaluation. Tout tourne en local, sur Apple Silicon, via MLX.

**Purge du 2026-09-13.** Sont définitivement abandonnés : les notes graduées (0-10, 1-5), les champs
hérités (`score`, `rationale`, `suggestsUnknown`, `hintCoverage`), et toute appréciation floue. Le
jugement repose exclusivement sur des **contrôles booléens atomiques** portant sur des faits observables,
débouchant sur un **verdict binaire strict**.

```
judge-finetune/
├── PROTOCOLE.md                     ← ce document
├── PROMPT_GENERATION.md             ← prompts pour déléguer la génération
├── Makefile                         ← toutes les commandes (make help)
├── data/
│   ├── seed/batch_NN.jsonl          ← source de vérité (messages + meta)
│   ├── PLAN_CORPUS.md               ← quotas, familles, avancement
│   ├── mlx/{train,valid,test}.jsonl ← généré par `make split` : messages seuls
│   └── golden/test.jsonl            ← généré par `make split` : golden set annoté
├── generators/                      ← construction déterministe des lots (`make regen`)
├── verification/                    ← preuves exécutables derrière chaque chiffre cité
└── scripts/                         ← dataset_tools.py, benchmark_judges.py, bench_variant.sh
```

Environnement vérifié : M3 Pro, 36 Go, `mlx-lm` 0.31.3. Les commandes MLX de ce document ont été
exécutées ou vérifiées via `--help`.

---

## 1. Les trois tâches et leurs postures

Un marqueur de tâche figure dans le message system de **chaque** exemple. Il sert à séparer des postures
de jugement qui sont, sur un point précis, contradictoires — et empêche la fuite paramétrique, c'est-à-dire
un juge qui accepte un fait halluciné parce qu'il le sait vrai par ailleurs.

| Marqueur | Posture | Ce que le juge doit faire |
|---|---|---|
| `CODE_ANALYSIS` | **Monde ouvert** | Mobiliser ses connaissances techniques pour détecter un défaut que la sortie ne mentionne pas (une `IllegalStateException` sur clé dupliquée, une traversée de répertoire…). |
| `RAG_CONTEXT_RELEVANCE` | Évaluation du moteur de recherche | Juger si les extraits récupérés suffisent à répondre, sans se prononcer sur la réponse elle-même. |
| `RAG_FAITHFULNESS` | **Monde fermé strict** | Ne juger qu'à partir du contexte fourni. Toute affirmation non étayée par un extrait est rejetée, **même si elle est vraie**. |

Les deux passes RAG sont **indépendantes** : elles permettent de diagnostiquer la cause d'un échec
(récupération insuffisante contre génération non ancrée), là où une note unique les confond.

### Contrôles atomiques par tâche

Chaque description énonce un fait observable, vérifiable sans jugement de goût.

**`CODE_ANALYSIS`**
- `exactitude_technique` — le code compile et s'exécute, les API utilisées existent, et chaque affirmation technique de la sortie est vraie.
- `absence_de_bugs` — aucun bug logique, faille de sécurité, régression ni erreur conceptuelle observable.
- `respect_consignes` — toutes les consignes obligatoires de la requête sont respectées.

**`RAG_CONTEXT_RELEVANCE`**
- `contexte_pertinent` — au moins un extrait porte directement sur les symboles ou notions visés.
- `contexte_suffisant` — les extraits contiennent toutes les informations nécessaires pour répondre entièrement.
- `bruit_maitrise` — le contexte ne noie pas l'information utile sous des extraits hors sujet.

**`RAG_FAITHFULNESS`**
- `affirmations_etayees` — chaque affirmation de la sortie est explicitement soutenue par un extrait.
- `absence_invention` — aucun symbole, signature, valeur ou comportement absent du contexte, même vrai par ailleurs.
- `citations_exactes` — les extraits cités ou paraphrasés correspondent fidèlement au contexte.

---

## 2. Schéma unifié

Une ligne JSON par exemple dans `data/seed/*.jsonl`, avec `meta` (retiré à l'export MLX) et `messages`.

```json
{"messages": [
  {"role": "system", "content": "Tu es un juge IA ultra-rigoureux. TÂCHE: CODE_ANALYSIS. Analyse la situation pas à pas dans <thinking> avant de rendre ton verdict JSON."},
  {"role": "user", "content": "### CONTEXTE / RAG\n…\n\n### ENTREE / REQUÊTE\n…\n\n### SORTIE À ÉVALUER\n…\n\n### CRITÈRES DE VALIDATION\n1. exactitude_technique: …\n2. absence_de_bugs: …\n3. respect_consignes: …"},
  {"role": "assistant", "content": "<thinking>\n1. …\n2. …\n3. … PASS.\n</thinking>\n{\n  \"checks\": {\"exactitude_technique\": true, …},\n  \"verdict\": \"PASS\",\n  \"reason\": \"…\"\n}"}
]}
```

### Règles invariantes, toutes vérifiées par `make validate`

1. **`verdict = "PASS"` si et seulement si tous les contrôles de `checks` valent `true`.** Aucune exception.
2. Les clés de `checks` sont **exactement** les critères déclarés dans la section `### CRITÈRES DE VALIDATION`,
   dans le même ordre. Le juge ne peut ni en inventer, ni en omettre.
3. Le `<thinking>` précède toujours le JSON, en trois étapes numérotées, et se termine par le même verdict.
4. Clés JSON exactement `checks`, `verdict`, `reason`, dans cet ordre.
5. `meta.cas = parfait` impose PASS, `meta.cas = defaillant` impose FAIL.

> **Pourquoi `checks` avant `verdict`.** Le modèle génère de gauche à droite. En plaçant les contrôles en
> tête, il doit inscrire chaque fait observable **avant** de sceller sa décision, et le verdict est produit
> en conditionnant sur des booléens déjà écrits. L'ordre inverse laisserait le modèle trancher d'abord puis
> justifier après, ce qui est exactement le comportement que ce corpus cherche à éliminer.

### Contrôles variables

Les trois contrôles listés par tâche sont un **socle**, pas une liste figée. Dès que la requête porte une
contrainte explicite et vérifiable, un contrôle dédié s'ajoute à la rubrique : `signature_conforme`,
`format_impose`, `dependance_autorisee`, `perimetre_respecte`, `contrainte_disponibilite`,
`aucune_dependance_externe`, `validation_entree`…

C'est une exigence, pas une facilité. Si toutes les rubriques d'une tâche étaient identiques, le juge
apprendrait le raccourci « marqueur de tâche → triplet figé » au lieu de lire la section
`### CRITÈRES DE VALIDATION`. Le corpus doit donc présenter plusieurs rubriques distinctes, **avec les deux
polarités** : un contrôle supplémentaire doit parfois valoir `true`, sinon le raccourci appris devient
« quatrième contrôle ⇒ échec ». État au 2026-09-13 : 8 rubriques distinctes sur 80 exemples, dont 8 exemples
à quatre contrôles répartis en 3 PASS et 5 FAIL.

### Contenu du `<thinking>`

Obligatoire, avant tout verdict. Trois étapes :

1. **Énumération** — symboles, méthodes, signatures en jeu ; pour les tâches RAG, citation **textuelle**
   des extraits pertinents du contexte.
2. **Vérification point par point** — chaque critère est confronté à un fait concret : un cas d'entrée et
   sa sortie, une exception nommée, un extrait cité, un plan d'exécution.
3. **Synthèse** — justification en une ou deux phrases, terminée par `PASS.` ou `FAIL.`

Un raisonnement générique n'apprend rien au juge. Aucun chiffre ne doit être inventé : toute mesure citée
provient d'un script de `verification/`.

### Champ `meta`

| Champ | Valeurs |
|---|---|
| `id` | `bNN-XXX`, unique |
| `famille` | slug du scénario — **anti-fuite** : les variantes d'un même scénario restent du même côté du split |
| `task` | `CODE_ANALYSIS` \| `RAG_CONTEXT_RELEVANCE` \| `RAG_FAITHFULNESS` |
| `domaine` | `code` \| `theorie` \| `rag` |
| `tache` | `generation`, `refactoring`, `debogage`, `explication`, `question_reponse`, `retrieval`, `synthese` |
| `cas` | `parfait` (⇒ PASS) \| `defaillant` (⇒ FAIL) \| `limite` (selon la gravité) |
| `verbeux` | booléen — base du test de biais de verbosité |
| `langage` | `java`, `python`, `typescript`, `sql`, `go`, `web`, … |

### Obligatoire contre facultatif

C'est la convention qui tranche les cas limites, et elle vaut pour les trois tâches :

| Situation | Effet |
|---|---|
| Consigne formulée comme préférence (« si possible », « si tu as le temps ») non suivie | contrôle à `true`, écart mentionné dans le `<thinking>` |
| Sortie verbeuse mais correcte | **jamais** pénalisée pour sa seule longueur |
| Exigence explicite et vérifiable non respectée (signature, version, dépendance interdite, format, périmètre) | contrôle à `false` |

---

## 3. Corpus

| | Cible 200 | Part |
|---|---|---|
| `CODE_ANALYSIS` | 150 | 75 % |
| `RAG_CONTEXT_RELEVANCE` | 25 | 12,5 % |
| `RAG_FAITHFULNESS` | 25 | 12,5 % |
| **RAG cumulé** | **50** | **25 %** |

Transversalement, sur l'ensemble du corpus : 40 % `parfait`, 40 % `defaillant`, 20 % `limite` ;
verdicts proches de 50/50 ; au moins 25 cas verbeux à défaut caché et 15 cas verbeux corrects en contrôle.

`train` + `valid` = 150 (dont 15 de validation, **obligatoire** pour `mlx_lm.lora --train`), `test` = 50.

### Matière RAG

Les contextes doivent être **réellement récupérés**, pas inventés : le dépôt contient déjà `QuestionCorpus`
(30 questions LOCAL / STRUCTURAL / CROSS_MODULE sur la codebase OllamAssist) et deux stratégies de
récupération. Un contexte synthétique produirait un juge entraîné sur des extraits trop propres, sans le
bruit, les doublons et les troncatures que produit une vraie recherche.

**Ce que ces 50 exemples visent — et ce qu'ils ne visent pas.** En production, l'évaluation RAG sera pilotée
par le prompt : c'est lui qui fournira le contexte et la rubrique. Les exemples RAG du corpus d'entraînement
n'ont donc pas à couvrir tous les modes de défaillance d'un moteur de recherche. Ils servent à enseigner
deux choses, et uniquement elles :

1. **La posture monde fermé**, c'est-à-dire rejeter une affirmation non étayée par le contexte, y compris
   lorsqu'elle est vraie. Le couple décisif à couvrir est une même affirmation acceptée sous
   `CODE_ANALYSIS` et rejetée sous `RAG_FAITHFULNESS`.
2. **La flexibilité du schéma JSON**, en présentant des rubriques dont les contrôles diffèrent de celles de
   `CODE_ANALYSIS`, pour que le juge lise la section `### CRITÈRES DE VALIDATION` au lieu de supposer un
   triplet figé.

Un jeu resserré et net sur ces deux points vaut mieux qu'un panorama exhaustif des pannes de récupération.

### Golden set

Les étiquettes sont produites par un modèle. Sans revue humaine, le κ mesure l'accord avec ce modèle, pas
avec des humains. Avant tout benchmark : deux annotateurs relisent `data/golden/test.jsonl` à l'aveugle,
on calcule le κ inter-annotateurs — c'est le **plafond** atteignable — et les désaccords sont arbitrés puis
reportés dans le lot source.

`data/golden/` et `data/mlx/` ne sont pas versionnés : ce sont des dérivés, reproductibles à l'identique
depuis les lots et la graine du tirage. Cette reproductibilité ne tient que parce que la graine est **figée
dans le `Makefile`** (`SPLIT_SEED ?= 3`) ; sans ce pin, deux annotateurs pourraient relire deux golden sets
différents sans s'en apercevoir. Attention au voisinage de noms : dans le `Makefile`, `SEED` désigne la
liste des lots JSONL, la graine du tirage est `SPLIT_SEED`.

Graine 3 et non le défaut 42 du script : le tirage est glouton et groupé par famille, donc il ne peut pas
couper une famille pour atteindre un quota, et la graine est le seul levier. Sur 15 graines essayées, 3
donne le golden set le plus proche des cibles (cas 20/20/10 au point près, 7 cas verbeux à défaut caché
sur 50, soit 14 % pour un plancher à 10 %) ; 42 était l'un des plus mauvais tirages. Le choix porte sur
des métadonnées déclarées — tâche, cas, verbosité — jamais sur des résultats de modèle.

Boucle de correction après relecture : toute étiquette corrigée passe par `generators/gen_batch_NN.py`
puis `make regen`, jamais par le JSONL. Si la correction change un `verdict` ou un `cas`, les strates du
tirage bougent : rejouer `make split` et relire le delta.

### Production d'un lot

```bash
make validate     # format, alignement critères/contrôles, cohérence du verdict — 0 erreur exigé
make stats        # dérive par tâche, par cas, verbosité
make regen        # reconstruit tous les lots depuis generators/ (aussi : réparation)
make split        # POC : make split-poc
```

Les JSONL ne s'éditent **jamais** à la main : une frappe accidentelle dans un éditeur a déjà corrompu un lot.

---

## 4. Fine-tuning local

Mêmes données, même quantification 4 bits, mêmes hyperparamètres pour les deux tailles : la seule variable
est le nombre de paramètres.

| Modèle | Disque | RAM |
|---|---|---|
| `Qwen2.5-Coder-0.5B-Instruct-4bit` (validation de chaîne) | 0,29 Go | 0,3 Go |
| `Qwen2.5-Coder-14B-Instruct-4bit` | 8,32 Go | ~8,3 Go |
| `Qwen2.5-Coder-32B-Instruct-4bit` | 18,44 Go | ~18,4 Go |

```bash
make smoke-all    # valide données → entraînement → service → benchmark sur le 0.5B (~3 min)
make train-14b    # adapters/14b-judge
make train-32b    # adapters/32b-judge
```

Derrière `train-14b`, flags vérifiés sur mlx-lm 0.31.3 :

```bash
.venv/bin/mlx_lm.lora --model mlx-community/Qwen2.5-Coder-14B-Instruct-4bit \
  --train --data data/mlx --fine-tune-type lora --mask-prompt \
  --batch-size 1 --grad-checkpoint --num-layers 16 \
  --iters 400 --learning-rate 1e-5 --max-seq-length 2048 \
  --steps-per-report 10 --steps-per-eval 50 --val-batches -1 \
  --adapter-path adapters/14b-judge --seed 42
```

Mesuré sur le 14B : ~11 s par itération, pic 11,08 Go, soit ~1 h 15 pour 400 itérations. Le 32B n'a pas
encore été entraîné ici ; en cas de saturation mémoire, réduire dans cet ordre `NUM_LAYERS=8` puis `MAXLEN=1024`.

Service : `mlx_lm.server --model … [--adapter-path …] --port …`, une variante à la fois, la somme des
quatre dépassant les 36 Go.

---

## 5. Benchmark

```bash
cp configs/variants.example.json configs/variants.json
make bench-14b && make bench-32b && make report
```

3 passes, T = 0,2, `max_tokens` 1024, bootstrap 2000. Les générations brutes sont mises en cache dans
`results/runs/` : une exécution interrompue reprend, et `make report` recalcule sans relancer l'inférence.

### Métriques

| # | Métrique | Définition |
|---|---|---|
| 1 | **κ de Cohen** (principale) | Accord des verdicts avec le golden set sur les 50 items, calculé par passe puis moyenné, avec IC95 par bootstrap. C'est **la** métrique de décision. |
| 2 | F1 | Classe positive `FAIL` (détection de défaut), plus macro-F1. Accord par **contrôle atomique** en diagnostic — c'est lui qui dit *quel* critère le juge rate. |
| 3 | Biais de verbosité | Faux PASS sur défauts verbeux contre défauts concis ; l'écart est le biais. Contrôle inverse sur les sorties verbeuses correctes. |
| 4 | Répétabilité | Part des items dont les 3 verdicts sont identiques et valides ; idem pour la décision complète (tous les contrôles + verdict). |
| 5 | Ressources | RAM, latence p50/p95, débit, temps pour 1000 jugements. Δκ apparié par bootstrap pour l'arbitrage 14B/32B. |

⚠️ **Le κ ne se décline pas par tâche sur ce golden set.** Le tirage y place 39 `CODE_ANALYSIS`, 5
`RAG_CONTEXT_RELEVANCE` et 6 `RAG_FAITHFULNESS` : un κ calculé sur 5 ou 6 items a un IC95 qui couvre
presque tout le domaine, et l'annoncer donnerait une précision que la mesure n'a pas. Il faudrait environ
25 items par tâche, donc un golden set d'une centaine — la moitié du corpus retirée de l'entraînement, ce
qui n'est pas soutenable à 200 exemples.

La posture monde fermé se surveille donc autrement, et il faut le faire explicitement, car c'est bien elle
que le fine-tuning vise : **rapporter les 11 items RAG en comptes bruts** (combien de verdicts corrects sur
11, et lesquels sont ratés), jamais en κ. Les trois cas décisifs sont ceux où la sortie est vraie dans la
codebase mais absente du contexte — ils doivent être rejetés. Un juge qui les accepte a manqué la posture,
et cela se voit sur 3 items sans avoir besoin d'un coefficient d'accord.

Parsing : tolérant pour le verdict (dernier objet JSON contenant `verdict`), strict mesuré à part comme
condition de qualification. Une sortie non parsable vaut `INVALID` et compte comme désaccord.

### Décision

**Qualification** — κ ≥ 0,60 ; stabilité du verdict ≥ 95 % ; format strict ≥ 95 % ; faux PASS sur verbeux ≤ 20 %.

**Gagnant** — le κ maximal parmi les variantes qualifiées.

**Arbitrage ressources** — le 32B n'est retenu que si la borne basse de l'IC95 du Δκ apparié est > 0 **et**
Δκ ≥ 0,05. Sinon le 14B l'emporte : 8,3 Go de RAM contre 18,4 déterminent si le juge peut tourner en tâche
de fond sur un poste de développement.

### Puissance statistique

Sur 50 items, l'IC95 d'un κ s'étend de ±0,15 à ±0,25 : deux variantes séparées de 0,05 sont indiscernables.
Seuls les **écarts appariés significatifs** permettent de conclure. Le κ par tâche, calculé sur ~12 items
chacune pour les passes RAG, est un signal qualitatif, pas une mesure.

---

## 6. Points ouverts

- Produire la matière RAG à partir de récupérations réelles (§3).
- Revue humaine du golden set et κ inter-annotateurs (§3).
- Mesurer la faisabilité du QLoRA 32B sur 36 Go (§4).
- Vérifier après fine-tuning que le juge bascule bien de posture selon le marqueur de tâche : le test
  décisif est une sortie RAG contenant une affirmation **vraie mais absente du contexte**, qui doit être
  rejetée sous `RAG_FAITHFULNESS` et acceptée sous `CODE_ANALYSIS`.
