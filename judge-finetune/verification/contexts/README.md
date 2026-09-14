# Contextes RAG réellement récupérés

Matière première des exemples `RAG_CONTEXT_RELEVANCE` et `RAG_FAITHFULNESS`. Ces fichiers rendent les
étiquettes vérifiables : chaque extrait cité dans un exemple se retrouve ici tel qu'il a été renvoyé.

Extraction du 2026-09-14 par `../ExtractRagContexts.java` sur `OllamAssist/src/main/java` (162 fichiers,
périmètre propre — voir l'avertissement sur la contamination dans `../../data/PLAN_CORPUS.md`).

| Fichier | Stratégie | Preset | Extraits/question | Contexte complet |
|---|---|---|---|---|
| `contextes-lucene-clean.jsonl` | Lucene | `hybrid` | 10 | 2 823 – 33 124 car. |
| `contextes-neo4j-clean.jsonl` | Neo4j | `hybrid-graph` | 5 | 837 – 2 886 car. |

Chaque ligne porte la question, sa difficulté, les indices attendus, la couverture calculée, la latence et
les extraits bruts. `couverture_indices` n'est qu'une présence de sous-chaîne : elle ne vaut pas jugement de
suffisance.
