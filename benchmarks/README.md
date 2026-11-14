# Résultats du banc d'essai RAG

Sorties de `RetrievalBenchmark` (JMH), **versionnées délibérément** : le dépôt est partagé pour
que la mesure soit reproductible, et des résultats laissés dans `target/` — répertoire de build,
ignoré par git — ne le permettraient pas.

| fichier | contenu |
|---|---|
| `jmh-judge.jsonl` | une ligne par (stratégie, scénario, fileCount, difficulté) |
| `jmh-judge-detail.jsonl` | une ligne par question : contexte récupéré, verdict, contrôles, motif |

## Le champ `schema`

Chaque ligne porte un marqueur de schéma. **`binaire-v1`** est le format actuel : verdict
`PASS`/`FAIL` avec ses trois contrôles atomiques, règle `PASS ⟺ tous les contrôles vrais`.

Il existait auparavant un juge à **note graduée 0-10** (`LLMJudge`, déprécié le 2026-09-21). Ses
lignes portaient `avgScore`, `unknownRate` et `rationale`, sans champ `schema`. **Les deux formats
ne se comparent pas** — une moyenne de notes et un taux de PASS ne mesurent pas la même chose.

Les écrivains ouvrent ces fichiers en **ajout**. Ne jamais mélanger deux schémas dans un même
fichier : archiver l'ancien sous un nom daté avant de changer de format.

## Reproduire

```bash
mvn test -Dtest=BenchmarkRunner#retrieval \
  -Drag.source.dir=/chemin/vers/OllamAssist/src/main/java \
  -Djmh.judge.provider=openai -Djmh.judge.url=http://127.0.0.1:8082/v1
```

Le juge doit être servi séparément — voir `judge-finetune/configs/variants.json` pour la variante
et son port.
