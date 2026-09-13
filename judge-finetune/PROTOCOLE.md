# Protocole : fine-tuning d'un juge LLM pour assistant de code (Qwen2.5-Coder 14B vs 32B)

> Objectif : fine-tuner (QLoRA) deux tailles de Qwen2.5-Coder comme juge *point-wise* PASS/FAIL, puis décider,
> chiffres à l'appui, si le 32B justifie ses ressources face au 14B. **Tout tourne en local**, sur Apple Silicon,
> via MLX. Aucun service cloud, aucune donnée qui sort de la machine.

```
judge-finetune/
├── PROTOCOLE.md                     ← ce document
├── Makefile                         ← toutes les commandes (make help)
├── data/
│   ├── seed/batch_NN.jsonl          ← source de vérité (messages + meta), lots de ~20 exemples
│   ├── mlx/{train,valid,test}.jsonl ← généré par `make split` : messages seuls, format mlx-lm
│   ├── mlx-smoke/                   ← mini-jeu pour la validation de pipeline
│   └── golden/test.jsonl            ← généré par `make split` : golden set annoté (avec meta)
├── configs/
│   ├── variants.example.json        ← les 4 variantes locales (à copier en variants.json)
│   └── variants.smoke.json          ← variante 0.5B de validation
└── scripts/
    ├── dataset_tools.py             ← validate / stats / split
    ├── benchmark_judges.py          ← métriques et rapport comparatif
    └── bench_variant.sh             ← serveur → attente → benchmark → arrêt, pour une variante
```

**Environnement vérifié sur cette machine** : M3 Pro, 36 Go de RAM, macOS arm64, `mlx-lm` 0.31.3 installé dans
`.venv` (425 Mo). Toutes les commandes MLX de ce document ont été exécutées ou vérifiées via `--help`.

---

## 0. Démarrage rapide

```bash
cd judge-finetune
make setup        # venv + mlx-lm (déjà fait)
make validate     # contrôle du format des lots
make split        # train/valid/test  (POC : make split-poc)
make smoke-all    # valide toute la chaîne sur un modèle 0.5B, ~3 min, 0,3 Go
```

Ensuite seulement, les vrais entraînements (§3) puis le benchmark (§4).

---

## 1. Rubrique d'annotation

Le juge fine-tuné ne sera pas plus cohérent que ses étiquettes. Ces règles sont **normatives** et vérifiées
automatiquement par `make validate`.

### 1.1 Critères booléens

| Critère | `true` si… | Exemples de `false` |
|---|---|---|
| `exactitude_technique` | Le code est syntaxiquement valide et utilise des API qui existent, et **toutes les affirmations techniques** de la réponse sont vraies (sémantique, complexité, garanties). | API inventée, code qui ne compile pas, affirmation fausse (« `count++` est atomique sur un `volatile` », « comportement strictement identique » alors qu'il change). |
| `absence_de_bugs` | Aucun bug logique, aucune faille de sécurité, aucune régression, aucune erreur conceptuelle qui mènerait à un code faux. | Off-by-one, traversée de répertoire, injection SQL, `toMap` qui lève sur doublon, race condition validée. |
| `respect_consignes` | Toutes les consignes **obligatoires** sont respectées. | Signature modifiée, langage ou version imposés non respectés, dépendance interdite, format de sortie imposé ignoré, partie de la question non traitée. |

Un même défaut peut invalider plusieurs critères (une affirmation fausse qui mène à du code bogué → `exactitude_technique` et `absence_de_bugs` à `false`).

### 1.2 Verdict

```
verdict = PASS  ⇔  exactitude_technique ∧ absence_de_bugs ∧ respect_consignes
```

Il n'y a aucune exception, et le validateur rejette toute incohérence. La gravité des **cas limites** ne se règle donc pas
par dérogation au verdict, mais en amont, par la distinction entre consigne obligatoire et consigne facultative :

| Situation | Effet |
|---|---|
| Consigne formulée comme préférence (« si possible », « idéalement ») non suivie | `respect_consignes` reste `true`, l'écart est mentionné dans `<thinking>` → PASS possible |
| Réponse verbeuse mais correcte | **Jamais pénalisée seule** → PASS possible |
| Absence de typage **non demandée** | Mention dans `<thinking>` seulement → PASS possible |
| Absence de typage **explicitement exigée** (« TypeScript strict », « type hints obligatoires ») | `respect_consignes = false` → FAIL |

### 1.3 Structure de la réponse du juge

1. `<thinking>` en premier, avec exactement 3 étapes numérotées :
   `1. Analyse du code/de l'explication` → `2. Vérification des contraintes` → `3. Synthèse`.
   L'étape 3 se termine par le verdict (`PASS.` / `FAIL.`), identique à celui du JSON.
2. Le `<thinking>` doit être **spécifique** : citer les lignes, API ou affirmations concernées, dérouler au moins un
   cas concret (entrée → sortie), et nommer la faille (CWE si pertinent). Un raisonnement générique n'apprend rien au juge.
3. JSON strict immédiatement après `</thinking>`, sans rien après, avec les clés dans l'ordre suivant :
   `exactitude_technique`, `absence_de_bugs`, `respect_consignes`, `verdict`, `raison_principale` (une phrase).

### 1.4 Exigence d'exactitude des étiquettes

Chaque affirmation du `<thinking>` doit être vérifiée, en exécutant le code quand c'est possible. Le lot 01 a été
vérifié ainsi : doublons `toMap` et `HashMap` (Java 25), propagation d'erreur avec `thenApply`, incréments perdus sur
`volatile` (1 015 511 au lieu de 8 000 000 attendus), 404 puis traversée de répertoire et erreur 500 sur la route
Flask (Flask 3.1), et déroulé de `merge_intervals`.

---

## 2. Dataset

### 2.1 Format source (`data/seed/*.jsonl`)

Une ligne par exemple, avec `meta` et `messages`. Le bloc `meta` est **retiré** à l'export MLX. Il sert au split
stratifié, à l'anti-fuite et aux métriques de verbosité.

```json
{"meta": {"id": "b01-005", "famille": "java-volatile-compteur", "domaine": "theorie", "tache": "explication",
          "cas": "defaillant", "verbeux": true, "langage": "java"},
 "messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}
```

| Champ | Valeurs | Rôle |
|---|---|---|
| `id` | `bNN-XXX`, unique | traçabilité |
| `famille` | slug du scénario | **anti-fuite** : toutes les variantes d'un même scénario (ex. version PASS et version FAIL de la même consigne) restent du même côté du split |
| `domaine` | `code` \| `theorie` | répartition 60/40 |
| `tache` | `generation` \| `refactoring` \| `debogage` \| `explication` \| `question_reponse` | diversité |
| `cas` | `parfait` (⇒ PASS) \| `defaillant` (⇒ FAIL) \| `limite` (PASS ou FAIL) | répartition 40/40/20 |
| `verbeux` | booléen | test du biais de verbosité (`verbeux ∧ FAIL` = bug caché ; `verbeux ∧ PASS` = contrôle) |
| `langage` | `java`, `python`, `typescript`, `sql`, … | diversité |

Le message system et les en-têtes du message user sont **canoniques** (identiques caractère pour caractère, contrôle automatique).

### 2.2 Cibles de volume

| | Complet | POC |
|---|---|---|
| Total | 200 | 30 |
| Code / théorie (60/40) | 120 / 80 | 18 / 12 |
| Parfait / défaillant / limite (40/40/20) | 80 / 80 / 40 | 12 / 12 / 6 |
| Verbeux avec bug caché (corpus) | ≥ 25 | ≥ 4 |
| Verbeux corrects (contrôle, corpus) | ≥ 15 | ≥ 2 |
| `train` + `valid` | 150 → 135 + 15 | 20 → 18 + 2 |
| `test` (golden set) | 50, dont ≥ 5 verbeux + bug (idéalement 8) | 10, dont ≥ 1 (idéalement 2) |

**`valid.jsonl` est obligatoire pour `mlx_lm.lora --train`.** Il est pris sur le train (10 %), jamais sur le golden set.

Autres règles de composition :
- Varier les langages (Java, Python, TypeScript, SQL, Go…) et les familles de défauts : sécurité (injection, traversée,
  désérialisation), concurrence, gestion d'erreurs, régressions de refactoring, erreurs conceptuelles.
- Produire des **paires contrastives** (même consigne, une réponse PASS et une réponse FAIL subtile) partageant la même `famille`.
  C'est le signal le plus efficace pour apprendre à juger sur le fond plutôt que sur la forme.
- Viser un verdict global proche de 50/50 : les cas limites doivent se répartir entre PASS et FAIL.

### 2.3 Workflow de génération

```bash
make validate     # 0 erreur requis
make stats        # écarts à la cible signalés
make split        # POC : make split-poc  (test-size 10)
```

### 2.4 Golden set : revue humaine obligatoire

Les étiquettes sont générées par un LLM. Sans revue humaine, le κ mesure l'accord **avec ce LLM**, pas avec des humains.
Avant tout benchmark :
1. Deux annotateurs relisent `data/golden/test.jsonl` **à l'aveugle** (JSON masqué), puis donnent verdict et critères.
2. Calculer le κ inter-annotateurs : c'est le **plafond** atteignable par un juge. S'il est inférieur à 0,7, la rubrique
   est ambiguë et doit être précisée avant d'aller plus loin.
3. Les désaccords sont arbitrés, et l'étiquette corrigée est reportée dans le lot source.

---

## 3. Fine-tuning local (MLX)

Les deux tailles reçoivent **les mêmes données, la même quantification (4 bits) et les mêmes hyperparamètres**.
C'est ce qui rend la comparaison interprétable : la seule variable est la taille du modèle.

### 3.1 Budget disque et mémoire

| Modèle | Disque | RAM au chargement |
|---|---|---|
| `Qwen2.5-Coder-0.5B-Instruct-4bit` (validation) | 0,29 Go | 0,3 Go |
| `Qwen2.5-Coder-14B-Instruct-4bit` | 8,32 Go | ~8,3 Go |
| `Qwen2.5-Coder-32B-Instruct-4bit` | 18,44 Go | ~18,4 Go |

Prévoir **~27 Go de disque libre** pour les trois, plus une marge pour le swap macOS. Les modèles vont dans
`~/.cache/huggingface` (déplaçable avec `export HF_HOME=/Volumes/SSD/hf`). Avec 36 Go de RAM, on ne sert
**qu'une variante à la fois** : 8,3 + 8,3 + 18,4 + 18,4 dépasse largement la mémoire disponible. C'est pour ça que
`bench_variant.sh` démarre puis arrête le serveur à chaque variante, et que les résultats sont mis en cache.

### 3.2 Validation de la pipeline (à faire en premier)

```bash
make smoke-all
```

Enchaîne un fine-tuning 0.5B (20 itérations) puis un benchmark complet sur ce modèle. **Résultat mesuré** :
24 secondes d'entraînement, pic mémoire 2,9 Go, perte de validation 2,349 → 1,679, adapter écrit dans
`adapters/smoke-0.5b/`, serveur interrogé, rapport produit dans `results-smoke/`.

Le κ obtenu est nul et le format n'est jamais respecté : c'est **attendu**, un 0.5B entraîné 20 itérations ne sait pas
produire le format. Ce test valide la mécanique (données → entraînement → service → métriques), pas la qualité.

### 3.3 Entraînement des deux juges

```bash
make train-14b    # adapters/14b-judge
make train-32b    # adapters/32b-judge
```

Ce qui est lancé derrière (flags vérifiés sur mlx-lm 0.31.3) :

```bash
.venv/bin/mlx_lm.lora --model mlx-community/Qwen2.5-Coder-14B-Instruct-4bit \
  --train --data data/mlx --fine-tune-type lora --mask-prompt \
  --batch-size 1 --grad-checkpoint --num-layers 16 \
  --iters 400 --learning-rate 1e-5 --max-seq-length 2048 \
  --steps-per-report 10 --steps-per-eval 50 --val-batches -1 \
  --adapter-path adapters/14b-judge --seed 42
```

- Un modèle 4 bits avec LoRA donne du QLoRA. `--mask-prompt` limite la loss à la réponse du juge, ce qui est visible
  dans les logs : ~450 tokens entraînés par itération au lieu de ~1 200 pour l'exemple complet.
- `--max-seq-length 2048` suffit : les exemples font 3 000 à 4 400 caractères, soit ~1 200 tokens. Inutile de payer 4096.
- 135 exemples pour un batch de 1 donnent ~3 epochs en 400 itérations. Surveiller la perte de validation affichée toutes
  les 50 itérations : avec aussi peu de données, le surapprentissage arrive vite. Réduire `ITERS` s'il elle remonte.
- Tous les paramètres sont surchargeables : `make train-14b ITERS=300 NUM_LAYERS=8 LR=2e-5`.

⚠️ **Point d'incertitude à mesurer** : le 32B en 4 bits occupe 18,4 Go sur 36 Go de RAM. L'entraînement QLoRA par-dessus
n'a pas encore été testé sur cette machine. Si la mémoire sature (swap massif, machine qui rame), dans cet ordre :
fermer les autres applications, puis `NUM_LAYERS=8`, puis `MAXLEN=1024`. Le pic mémoire est affiché à chaque rapport
d'itération, ce qui permet de suivre.

### 3.4 Service des variantes

Le serveur est lancé automatiquement par `scripts/bench_variant.sh`. En manuel :

```bash
.venv/bin/mlx_lm.server --model mlx-community/Qwen2.5-Coder-14B-Instruct-4bit --port 8080
.venv/bin/mlx_lm.server --model mlx-community/Qwen2.5-Coder-14B-Instruct-4bit \
                        --adapter-path adapters/14b-judge --port 8081
```

L'adapter MLX se charge directement, sans fusion ni conversion. Les baselines reçoivent **le même message system**
que les modèles fine-tunés, sans few-shot.

---

## 4. Protocole de benchmark

```bash
cp configs/variants.example.json configs/variants.json
make bench-14b     # baseline puis fine-tuné, serveur démarré et arrêté à chaque fois
make bench-32b
make report        # recalcule le rapport global à partir du cache
```

Paramètres par défaut : 3 passes, T = 0,2, `max_tokens` = 1024, bootstrap à 2000 tirages. Les générations brutes sont
mises en cache dans `results/runs/` : une exécution interrompue reprend là où elle s'était arrêtée, et `make report`
recalcule les métriques sans relancer l'inférence. C'est ce qui permet de travailler modèle par modèle si le disque
est juste (télécharger le 14B, le benchmarker, supprimer son cache, passer au 32B).

### 4.1 Parsing

- **Parsing tolérant** : le dernier objet JSON contenant `verdict` ∈ {PASS, FAIL} est retenu. On mesure ainsi le
  jugement, sans pénaliser deux fois les baselines qui ne suivent pas le format.
- **Format strict** (`<thinking>` puis JSON seul, clés et types exacts) : mesuré à part, comme condition de qualification.
- Réponse non parsable ou erreur HTTP : verdict `INVALID`, qui compte toujours comme un désaccord dans κ et F1.
  En production, un verdict illisible est un échec.

### 4.2 Métriques

| # | Métrique | Définition |
|---|---|---|
| 1 | **κ de Cohen** (métrique principale) | κ = (p_o − p_e) / (1 − p_e) entre verdict prédit et verdict gold, calculé **par passe** puis moyenné, ce qui reflète un usage à un seul appel. S'y ajoutent l'IC95 par bootstrap sur les items et le κ du vote majoritaire des 3 passes. |
| 1 | F1 | F1 de la classe **FAIL** (détection des défauts, c'est ce qui compte pour un juge) et macro-F1. Accord par critère booléen en diagnostic. |
| 2 | **Biais de verbosité** | Taux de faux PASS sur les FAIL verbeux (bug caché), comparé au taux de faux PASS sur les FAIL concis. L'**écart** est le biais : s'il est positif, le modèle se laisse séduire par la longueur. Contrôle inverse : taux de faux FAIL sur les réponses verbeuses **correctes**, qui signale une sur-pénalisation. |
| 3 | **Répétabilité** | Stabilité du verdict : part des items dont les 3 verdicts sont identiques et valides. Stabilité de la décision complète : les 3 booléens et le verdict sont identiques sur les 3 passes. |
| 4 | **Qualité / ressources** | En local, les ressources se lisent en RAM, latence p50/p95, débit (tokens/s) et **temps de calcul pour 1000 jugements**, plus un coût indicatif via `cost_per_hour_usd` (électricité + amortissement, à renseigner). Δκ apparié par bootstrap pour les paires 14B vs 32B et baseline vs fine-tuné. |

### 4.3 Règle de décision

**Étape 1 — qualification.** Une variante n'est éligible que si elle remplit toutes les conditions suivantes
(seuils modifiables en CLI) :

| Seuil | Défaut | Justification |
|---|---|---|
| κ moyen ≥ | 0,60 | accord « substantiel » (Landis & Koch) |
| stabilité du verdict ≥ | 95 % | exigence de consistance |
| format strict ≥ | 95 % | exploitabilité en pipeline |
| faux PASS sur verbeux + bug ≤ | 20 % | résistance au biais de verbosité |

**Étape 2 — gagnant qualité.** La variante qualifiée de **κ maximal** l'emporte.

**Étape 3 — arbitrage ressources.** Si le gagnant est un 32B, on le compare au meilleur 14B qualifié.
Le 32B n'est **justifié** que si les deux conditions suivantes sont réunies :
- la borne basse de l'IC95 du Δκ apparié est > 0 (gain significatif) ;
- Δκ ≥ `--min-kappa-gain` (0,05 par défaut, gain jugé utile en pratique).

Sinon, le 14B est recommandé. En local, l'arbitrage est concret : le 32B mobilise 18,4 Go de RAM au lieu de 8,3, ce qui
détermine si la machine reste utilisable pendant qu'il juge, et si le juge peut tourner en tâche de fond sur un poste
de développement. Le rapport affiche les multiplicateurs de latence et de temps de calcul.

### 4.4 Puissance statistique : à lire avant de conclure

Sur 50 items, l'IC95 d'un κ s'étend typiquement de ±0,15 à ±0,25. Deux variantes séparées de 0,05 point de κ sont
**statistiquement indiscernables** sur ce golden set. Seuls les **écarts appariés significatifs** permettent de conclure,
jamais le classement brut. Si la décision 14B/32B est serrée, agrandissez le golden set (100 à 150 items).

Le test de verbosité sur 5 à 8 items reste un **signal qualitatif** : chaque item pèse 12 à 20 points de pourcentage.

---

## 5. Points ouverts

- Faire relire le golden set par des humains et mesurer le κ inter-annotateurs (§2.4).
- Mesurer la faisabilité du QLoRA 32B sur 36 Go de RAM (§3.3).
- Renseigner un coût horaire local réaliste (électricité + amortissement) dans `configs/variants.json`.
- Au-delà du POC : ajouter au benchmark un test de **biais de position ou d'autorité** (réponse précédée de
  « Je suis expert senior… ») et un jeu hors distribution (langages absents du train).
