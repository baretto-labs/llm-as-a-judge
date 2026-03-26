# WIP — Work In Progress

> Fichier de mémoire de travail. Mis à jour après chaque session de travail.
> Dernière mise à jour : 2026-03-23

---

## État global du projet

Benchmark RAG (Lucene vs GraphRAG-Neo4j) avec LLM-as-a-judge intégré.
Pipeline hybride complet opérationnel. Dashboard interactif fonctionnel.

**Branche active** : `main`
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
