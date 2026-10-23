# Pré-enregistrement — notation graduée contre verdict binaire

**Écrit le 2026-10-19, avant tout jugement.** Le tirage des 12 items est fait et figé
(`benchmarks/notation/items.json`) ; aucun jugement n'a encore été rendu au moment d'écrire ces
lignes.

## Question

Une note graduée est-elle **plus instable** qu'un verdict binaire quand on permute l'ordre des
extraits du contexte, toutes choses égales par ailleurs ?

## Ce que la mesure ne peut pas dire

Les 12 items n'ont **aucune étiquette de référence**. Cette expérience mesure la **stabilité**,
jamais la justesse. Une note parfaitement stable peut être parfaitement fausse.

## Dispositif

| | |
|---|---|
| Items | 12, tirés avec graine `20261019`, 4 par bras, stratifiés par difficulté |
| Juge | `qwen2.5-coder:32b` + `judge-finetune/configs/conventions.md`, Ollama, température 0 |
| Format A | `{checks{3 booléens}, verdict: PASS\|FAIL, reason}` — le schéma de la campagne |
| Format B | `{checks{3 booléens}, note: entier 0–10, reason}` — **seul le champ final change** |
| Passes | 5 par item et par format : **2 à ordre identique** (témoin), **3 à ordres permutés** |
| Total | 120 jugements, ≈ 1 h 30 à 43 s/jugement |

**Pourquoi les `checks` restent dans les deux formats.** Pour qu'une seule chose change entre A et
B. Si la note bougeait plus parce qu'elle est demandée seule, sans ancrage, on mesurerait l'absence
d'ancrage et non l'échelle.

**Contrainte de sélection, et sa raison.** `RagContextJudge` tronque le contexte à 6000 caractères
**après** mélange : sur un item plus long, permuter ne change pas l'ordre mais **le contenu qui
survit**. Les 12 items ont donc tous un contexte joint ≤ 6000 caractères et ≥ 3 extraits. La
permutation y est un changement d'ordre **pur**.

**Ordre de base** : celui du moteur, tel que stocké dans `context`. Les 3 permutations sont tirées
avec la graine `hash(question) + indice de passe`, donc rejouables.

## Comparaison loyale : on compte des décisions, pas des échelles

Une note à 10 niveaux bouge mécaniquement plus qu'un booléen. On binarise donc la note à un seuil
**fixé ici, avant de voir le moindre résultat** : **note ≥ 7 ⇒ PASS**. On compte des
**retournements de décision** des deux côtés, sur les 3 passes permutées.

Métrique principale : **nombre d'items (sur 12) dont la décision n'est pas identique sur les 3
permutations**, pour A et pour B.

Métriques de couleur, jamais seules à l'écran : dispersion de la note (max − min) par item, et
nombre d'items dont la note varie d'au moins 2 points.

## Lecture, fixée avant de lancer

| Témoin (2 passes à ordre identique) | conduite |
|---|---|
| ≥ 1 retournement, format A ou B | **expérience invalide**, rien ne va à l'écran : le service n'est pas déterministe, la permutation n'est plus la seule cause possible |
| 0 retournement | l'expérience est lisible, on applique le tableau suivant |

| Retournements de décision, B (note) contre A (binaire) | conduite |
|---|---|
| B ≥ 3 × A | **le chiffre va à l'écran** : la notation est la source d'instabilité |
| 1 × A < B < 3 × A | chiffre brut rapporté, **aucune leçon** tirée à l'écran |
| B ≤ A | **rien ne va à l'écran** ; la leçon pressentie est fausse et on l'aura appris avant la scène |

Cas particulier déclaré d'avance : si **A = 0**, le rapport B/A n'existe pas. On applique alors le
seuil absolu **B ≥ 3 items sur 12 ⇒ le chiffre va à l'écran**, B ∈ {1, 2} ⇒ chiffre brut sans
leçon, B = 0 ⇒ rien.

## Les 12 items

| # | bras | difficulté | extraits | question |
|---|---|---|---|---|
| 1 | vector | CROSS_MODULE | 5 | How does OllamAssistStartup initialize EditorListener on project load? |
| 2 | vector | LOCAL | 5 | What does the calculateDynamicThreshold method compute in LuceneEmbeddingStore? |
| 3 | vector | STRUCTURAL | 5 | What does DocumentIndexingPipeline implement? |
| 4 | vector | CROSS_MODULE | 5 | How does RAGConfigPanel trigger a full reindexation of the project? |
| 5 | vector-bm25 | CROSS_MODULE | 10 | How does DocumentIngestFactory authenticate its requests to Ollama? |
| 6 | vector-bm25 | LOCAL | 10 | What does the calculateDynamicThreshold method compute in LuceneEmbeddingStore? |
| 7 | vector-bm25 | STRUCTURAL | 10 | What interfaces does OllamaService implement? |
| 8 | vector-bm25 | STRUCTURAL | 10 | What class extends AnAction for the refactoring feature? |
| 9 | graphrag | CROSS_MODULE | 5 | How does AddToContextAction add a selected file to the workspace context? |
| 10 | graphrag | LOCAL | 5 | What constants does DocumentIndexingPipeline define for batch processing? |
| 11 | graphrag | STRUCTURAL | 5 | What does LuceneEmbeddingStore implement? |
| 12 | graphrag | CROSS_MODULE | 5 | How does AskFromCodeAction notify the chat UI via NewUserMessageNotifier? |

---

## Résultat, 2026-10-19 — lecture appliquée telle qu'écrite

120 jugements, **0 en échec**. Témoin propre : **0 retournement** à ordre identique, des deux
côtés — le service est déterministe, la permutation était bien la seule cause possible.

| | retournements de décision sur 3 permutations |
|---|---|
| A — verdict binaire | **0 / 12** |
| B — note binarisée à ≥ 7 | **0 / 12** |

Règle du seuil absolu (A = 0, B = 0) ⇒ **rien ne va à l'écran**. L'hypothèse de départ — la
notation est plus instable que le binaire sous permutation — **n'est pas confirmée** dans ces
conditions. Amplitude des notes : **0 sur les 12 items**.

Ce que ce résultat ne dit pas : la littérature observe l'instabilité surtout en échantillonnage
(température > 0) et en **comparaison par paires** (biais de position A/B). Ici, température 0,
décodage contraint, notation d'un item isolé, contextes courts non tronqués. Le dispositif est
donc le cas le plus favorable à la stabilité, et il ne réfute pas la littérature : il ne la
reproduit pas.

### Observations post hoc, non pré-enregistrées, donc non présentables en l'état

- Les deux formats rendent la **même décision sur 12 items / 12**.
- La note ne prend que **4 valeurs** sur 60 jugements : 1 (×35), 6 (×10), 10 (×10), 0 (×5).
  L'échelle à 11 niveaux se comporte comme une échelle à trois crans. C'est un défaut de la
  notation, mais **ce n'est pas celui qui était pré-enregistré** : le promouvoir à l'écran
  exigerait un nouveau pré-enregistrement et une mesure dédiée.
