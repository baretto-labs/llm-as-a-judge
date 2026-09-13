# WIP — Work In Progress

> Fichier de mémoire de travail. Mis à jour après chaque session de travail.
> Dernière mise à jour : 2026-09-11

---

## Sous-projet `judge-finetune/` — fine-tuning d'un juge Qwen2.5-Coder 14B vs 32B (démarré 2026-09-11)

Tout le détail est dans `judge-finetune/PROTOCOLE.md`.

**Complété**
- Rubrique d'annotation normative : verdict PASS ⇔ les 3 critères à `true`. La gravité des cas limites est gérée par la distinction consigne obligatoire / facultative.
- Lot `data/seed/batch_01.jsonl` : 5 exemples (3 code / 2 théorie ; 2 parfaits / 2 défaillants / 1 limite), faits vérifiés par exécution (Java 25, Flask 3.1).
- `scripts/dataset_tools.py` : validate / stats / split. Le split est stratifié et groupé par `famille` (anti-fuite), exporte au format MLX sans `meta` et produit un `valid.jsonl` (obligatoire pour mlx-lm).
- `scripts/benchmark_judges.py` : κ, F1, biais de verbosité, répétabilité sur 3 passes, RAM/latence/débit, Δκ apparié par bootstrap, règle de décision. Testé contre un serveur mock puis en réel.
- Interface shell : `Makefile` (`make help`) + `scripts/bench_variant.sh` (serveur → attente → benchmark → arrêt). Python uniquement là où il apporte quelque chose ; stdlib seule, aucune dépendance.
- `.venv` avec mlx-lm 0.31.3. Tous les flags MLX du protocole sont vérifiés, plus par mémoire.
- **Pipeline validée de bout en bout** sur Qwen2.5-Coder-0.5B-4bit (`make smoke-all`) : entraînement 20 itérations en 24 s, pic 2,9 Go, val loss 2,349 → 1,679, puis service avec adapter et benchmark complet. Le 0.5B sort du JSON sans `<thinking>` ni `verdict` (κ = 0) : attendu, la mécanique est validée, pas la qualité.
- `generators/` et `verification/` versionnés : chaque lot est reproductible au bit près (`make regen`, vérifié), et chaque chiffre cité dans un `<thinking>` provient d'un script exécutable du dossier `verification/`. Les JSONL ne s'éditent jamais à la main — une frappe accidentelle dans l'IDE a déjà corrompu le lot 04, restauré par régénération.

**Décisions**
| Décision | Rationale |
|---|---|
| Tout en local (MLX), plus de cloud GPU | Demande utilisateur ; supprime aussi le biais 4 bits vs bf16 entre les deux tailles |
| Une variante servie à la fois | 8,3 + 8,3 + 18,4 + 18,4 Go > 36 Go de RAM ; le cache `results/runs/` permet de travailler modèle par modèle |
| `meta` dans les lots source, retiré à l'export MLX | Nécessaire au split stratifié, à l'anti-fuite par famille et aux métriques de verbosité |
| κ calculé par passe puis moyenné (+ κ du vote majoritaire en complément) | Reflète l'usage en production (un seul appel) |
| Parsing tolérant pour κ, format strict mesuré à part ; INVALID = désaccord | Sépare la qualité du jugement du respect du format, sans masquer les sorties inexploitables |
| `--max-seq-length 2048` et non 4096 | Exemples mesurés à ~1 200 tokens ; économise de la mémoire |
| Le 32B n'est justifié que si la borne basse de l'IC95 du Δκ est > 0 et Δκ ≥ 0,05 | Avec n = 50, les écarts de κ bruts ne sont pas interprétables |
| Génération déléguée possible, étiquetage non | La diversité des réponses à juger réduit le biais d'auto-préférence et rapproche la distribution de la production ; l'hétérogénéité des verdicts, elle, ajoute du bruit d'étiquetage qui plafonne le κ atteignable |
| Trois catégories de `cas`, deux verdicts | `parfait` ⇒ PASS, `defaillant` ⇒ FAIL, `limite` réparti selon la gravité (11 PASS / 5 FAIL à 80 exemples) — pas de verdict intermédiaire |

**Prochaines étapes**
1. ~~Libérer du disque~~ : fait le 2026-09-12, 159 Go récupérés (caches dev, modèles Ollama, VMs UTM, VM Colima purgée). 220 Go libres.
2. Générer les 200 exemples — **80/200 faits** (batch_01 : 5, puis 15 par lot). Prompts pour déléguer la génération à des modèles tiers : `judge-finetune/PROMPT_GENERATION.md`. Méthode par lot : sonder les comportements par exécution, écrire les exemples à partir des sorties mesurées, valider, contrôler la dérive de distribution. Plan de composition et familles dans `data/PLAN_CORPUS.md`. Le 14B a été sondé sur 20 itérations : ~11 s/itération, pic 11,08 Go, soit ~1 h 15 pour 400 itérations.
3. Faire relire le golden set par des humains et calculer le κ inter-annotateurs, qui sert de plafond.
4. Mesurer la faisabilité du QLoRA 32B sur 36 Go (repli : `NUM_LAYERS=8`, puis `MAXLEN=1024`).

---

## État global du projet

Benchmark RAG (Lucene vs GraphRAG-Neo4j) avec LLM-as-a-judge intégré.
Pipeline hybride complet opérationnel. Dashboard interactif fonctionnel.

**Branche active** : `feat/judge-finetune-dataset` (poussée sur origin)
**Objectif immédiat** : démo équipe ~20 minutes

---

## Périmètre démo (ne pas toucher avant la démo)

Ce qui **fait** le message en 20 minutes :

| Élément | Fichier clé |
|---|---|
| Latence Lucene vs Neo4j sur 4 scénarios | Dashboard — section Performance |
| Feature flags knn-only → hybrid → hybrid-graph → hyde | `FeatureFlags.java` |
| Score LLM-as-a-judge + rationale | Dashboard — section LLM-as-a-judge |
| Panneau dépliable question / contexte généré / attendu / score | Dashboard — tableau détaillé |
| 30 questions (10 LOCAL / 10 STRUCTURAL / 10 CROSS_MODULE) | `QuestionCorpus.java` |
| Multi-juge via `-Djmh.judge.models=m1,m2` | `LLMJudge.java` |

**Narrative démo (20min)** :
1. Le problème — comment mesurer objectivement la qualité RAG ? (2min)
2. Setup — Lucene vs Neo4j, feature flags pour isoler chaque optimisation (3min)
3. Résultats perf — latence, coût du graphe (5min)
4. Résultats qualité — LLM-as-a-judge, ouvrir des lignes du tableau (7min)
5. Suite possible — mentionner le backlog en 1 phrase par item (3min)

---

## Surplus implémenté — disponible mais hors démo

Code en place, fonctionnel, à mettre en avant **après** la démo si l'équipe veut approfondir.

| Feature | Où | Activation |
|---|---|---|
| Few-shot dans le prompt juge | `LLMJudge.java` — `@SystemMessage` | Toujours actif |
| Position bias mitigation (shuffle chunks) | `LLMJudge.judge()` | Toujours actif |
| RRF K configurable | `FeatureFlags.rrfK` (défaut 60) | Via preset custom |
| Script stats Mann-Whitney + BH | `scripts/stats.py` | `python3 scripts/stats.py` |
| Chart Score vs fileCount | Dashboard — section judge | Si fileCount > 1 |

---

## Backlog post-démo

### B1 — Statistiques

- **Kappa inter-juges** : calculer Cohen's kappa dans `scripts/stats.py` entre les deux juges du multi-juge. Si kappa < 0.6, les juges divergent trop.
- **Baseline naïve** : ajouter une stratégie `random` top-K pour avoir une borne inférieure (un score 7/10 est-il bon ?). `RetrievalBenchmark.java` + `FeatureFlags.java`.

### B2 — Pipeline RAG

- **Multi-query retrieval** : générer N variantes de la question avant la recherche, fusionner avec RRF. `Neo4jGraphRagStrategy.java`, `HybridSearchService.java`.
- **Cross-encoder reranker** : remplacer `LLMReranker` par BGE-Reranker local. 10-50x plus rapide.
- **Embeddings sur Package/Import/Property** : étendre les index vectoriels Neo4j.

### B3 — GraphRAG

- **Community summarization** : générer un résumé LLM par communauté et l'indexer. `CommunityDetection.java`.
- **Versioning schéma graphe** : nœud `Project` avec version + re-indexation forcée.
- **Construction du graphe via bytecode** (priorité haute) : remplacer JavaParser par ASM/ByteBuddy pour parser les `.class` compilés. JavaParser rate les lambdas, méthodes de référence et classes anonymes → relations CALLS/EXTENDS incomplètes → K-hop expansion inutile. Le bytecode est non-ambigu et donne un graphe de qualité production. Le contexte retourné au LLM reste du source Java (lisible). Résultat attendu : Neo4j rattrape ou dépasse Lucene sur les questions CROSS_MODULE. `Neo4jGraphRagStrategy.java`.

### B4 — Benchmark avancé

- **Comparaison embedding models** : `@Param embeddingModel` dans `RetrievalBenchmark`. Tester voyage-code-3, jina-embeddings-v3.

---

## Décisions d'architecture

| Décision | Rationale | Date |
|---|---|---|
| HyDE uniquement sur le vecteur (pas BM25) | Le code Java généré casse le parser Lucene/Neo4j fulltext | 2026-03-19 |
| hintCoverage programmatique (pas LLM) | Le LLM peut halluciner "j'ai vu X" — mesure déterministe préférable | 2026-03-19 |
| Structured output via AiServices (pas regex) | Élimine les bugs de parsing, type safety garantie | 2026-03-19 |
| @Threads(1) sur RetrievalBenchmark | État partagé (pending*, listes) non thread-safe | 2026-03-19 |
| JSONL par (strategy, scenario, fileCount, difficulty) | Granularité dashboard, évite agrégation client-side | 2026-03-19 |
| Panel indépendant (pas délibératif) pour multi-juge | Évite la sycophancy, standard MT-Bench/LMSYS | 2026-03-19 |

---

## Questions ouvertes

- Quel est le vrai critère de succès pour l'équipe : latence ? qualité ? les deux ? -> les deux
- Le scope inclut-il une étape de génération (RAG complet) ou on reste sur le retrieval ? - RAGcomplet
- Après la démo : publier les résultats en interne ou continuer d'itérer d'abord ? -> à voir
