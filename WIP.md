# WIP — Work In Progress

> Mémoire de travail. Mise à jour après chaque session.
> Dernière mise à jour : 2026-10-14
>
> **L'historique détaillé n'est plus ici.** Il vit dans les documents qui font foi :
> `judge-finetune/REX_TRAME.md` (tous les chiffres), `AUDIT.md` (les défauts du corpus),
> `PREENREGISTREMENT.md` et `PREENREGISTREMENT_RELECTURE2.md` (ce qui a été déclaré avant mesure),
> `data/REVUE_GOLDEN.md` (la relecture), `PROTOCOLE.md` (la méthode), `TRIAGE_POSTHOC.md`.

---

## Où on en est

Benchmark RAG (Lucene vs GraphRAG-Neo4j) jugé par un LLM entraîné et servi en local.
**Le code est figé. Tout le travail restant est éditorial.**

**Branche active** : `talk/v1`
**Objectif** : l'exposé de **novembre 2026 — DevFest Paris, 20 min, ~400 personnes**.

### Chemin critique — ces trois tâches seules décident si l'exposé existe

1. **Reformuler** les 25 diapositives sur 33 encore écrites dans les mots de l'assistant.
2. **Couper** ~12 minutes : le support fait ~32 min de script pour un créneau de 20.
3. **Dessiner** les dix états du schéma de construction du juge (échafaudage ASCII en place dans
   `demo/CONFERENCE-V2.md`, versions longues dans `demo/SCHEMA-ETATS.md`).

Tout le reste améliore sans être indispensable.

### En cours, et qui ne se rattrape pas

**Seconde relecture du golden set par un collègue.** Pré-enregistrée le 2026-10-14, paquet aveugle et
feuille de réponses générés dans `judge-finetune/data/relecture2/`. Objectif :
**κ(relecteur 1, relecteur 2)**, le vrai accord inter-humain — celui que le support revendiquait sans
l'avoir. **Seule tâche qui dépend de quelqu'un d'autre.**

---

## Ligne éditoriale de l'exposé, arrêtée le 2026-10-14

C'est un **REX** : approche, théorie, conclusions — pas tout. Le **κ est rétrogradé au rang de
diagnostic** ; porté par deux diapositives, il donnait à l'ensemble une couleur d'excuse.

**Règle de coupe : enlever la méthode, garder la preuve.** Ces quatre chiffres ne se coupent pas, ce
sont les faits que personne d'autre ne possède :

| | |
|---|---|
| conventions | **0 % → 76 %** de justesse, pour quatre paragraphes |
| le banc RAG | **48,3 % contre 23,7 %**, témoin invariant à la décimale, corroboré sans LLM |
| le triage | **12 relectures au lieu de 50** |
| les sondes | **cinq fois** un banc qui mesure le vide en affichant BUILD SUCCESS |

**Posture** : l'aveu est une preuve, jamais le propos. Et le sujet de la phrase est celui qui **détecte**,
pas celui qui échoue — « mon banc a mesuré le vide » devient « je l'ai attrapé cinq fois ».

---

## Décisions qui lient encore

| Décision | Rationale |
|---|---|
| Exactitude seule, verdict binaire | Réorientation du 2026-09-13. Notes graduées et champs hérités (`score`, `rationale`, `suggestsUnknown`) abandonnés, ainsi que `scripts/stats.py` et les dashboards qui les consomment |
| `<thinking>` puis `{checks, verdict, reason}` | La génération est séquentielle : le modèle pose les faits avant de trancher. PASS ⇔ tous les `checks` à `true` |
| Jamais d'édition manuelle d'un JSONL | Tout passe par `generators/gen_batch_NN.py` puis `make regen`. Une frappe dans l'IDE a déjà corrompu le lot 04 |
| Tout en local (MLX), une variante servie à la fois | 8,3 + 8,3 + 18,4 + 18,4 Go > 36 Go de RAM |
| Paires de comparaison **déclarées** dans `configs/variants.json` | Jamais inférées après coup |
| Aucune règle d'arbitrage entre tailles 14B/32B | L'écart est rapporté avec son intervalle, sans verdict. En inventer une après coup reviendrait à choisir la règle une fois les chiffres connus |
| Génération déléguée possible, étiquetage non | L'hétérogénéité des verdicts ajoute du bruit qui plafonne le κ atteignable |
| HyDE uniquement sur le vecteur, pas BM25 | Le code Java généré casse le parser fulltext |
| `hintCoverage` programmatique, pas LLM | Un LLM peut halluciner « j'ai vu X » ; corrobore un **classement**, ne valide pas le juge |
| Panel indépendant, pas délibératif | Évite la sycophancy — standard MT-Bench |

---

## Questions ouvertes

- **Matrice de la diapositive 14** — celle affichée (16 recalés / 11 passés / 22 validés) est celle du
  **fine-tuné**, alors que l'exposé raconte la variante à conventions. Récupérer l'équivalent depuis
  `results/runs/`, ou introduire le fine-tuning plus tôt. **Dernier arbitrage ouvert du support.**
- **Réparer le test de verbosité** — `AUDIT.md` §2 : les deux groupes ne se chevauchent pas en longueur,
  et sur 40 familles du golden **3 seulement** portent les deux longueurs, donc l'appariement que la
  diapositive annonce n'existe pas. Correctif : jeu dédié `data/verbosity/`, **hors du tirage** — sinon
  `make split` redessine le golden set et change les 50 items du second relecteur en cours de route.
  Design apparié, 10 cas de base rendus en version bavarde et concise, McNemar sur les paires. Bonus.
- **Bug latent** — le preset `hybrid-graph-hyde` pose `hydeEnabled=true` et `rerankingEnabled=false`, or
  `Neo4jGraphRagStrategy.java:246` ne branche le modèle HyDE que si le reranking est actif. Ce preset
  tournerait **sans HyDE** en annonçant son nom. Jamais publié, donc rien d'invalidé.
- **Abandonné pour l'exposé, versé à l'article de blog** : le jury multi-modèles (sous-dimensionné — il
  faudrait rattraper 10 des 12 désaccords pour conclure) et `citations_exactes` dégénéré (vrai 25 fois
  sur 25).

---

## Backlog technique, après l'exposé

- **Construction du graphe via bytecode** (ASM/ByteBuddy au lieu de JavaParser) — *priorité haute*.
  JavaParser rate lambdas, références de méthode et classes anonymes, donc les relations CALLS/EXTENDS
  sont incomplètes et l'expansion K-hop travaille sur un graphe troué. C'est la piste la plus crédible
  pour que Neo4j rattrape Lucene sur CROSS_MODULE — le seul niveau où l'écart conclut aujourd'hui.
- **Cross-encoder reranker** local (BGE) à la place de `LLMReranker` : 10 à 50× plus rapide.
- **Multi-query retrieval** : N variantes de la question, fusion RRF.
- **Comparaison de modèles d'embedding** : voyage-code-3, jina-embeddings-v3.
