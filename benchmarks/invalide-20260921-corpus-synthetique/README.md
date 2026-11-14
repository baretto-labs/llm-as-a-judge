# Run invalidé du 2026-09-21 — à ne pas lire comme un résultat

Ces deux fichiers sont conservés comme pièce, **pas comme mesure**. Trois défauts, tous
constatés après coup :

1. **Le corpus indexé n'était pas celui des questions.** `-Drag.source.dir` n'atteignait pas la
   JVM de test — surefire n'avait aucune configuration et ne transmettait pas les `-D`. Le banc a
   donc indexé le corpus synthétique `com.example.service.Class0Service` pendant que les
   60 questions portaient sur OllamAssist. D'où `hintCoverage = 0,000` partout, et un `passRate`
   de 0 % : le juge avait raison de tout rejeter.
2. **Le jugement était interrompu à mi-parcours.** Il tournait dans `@TearDown(Level.Trial)` de
   JMH, dont l'échéance est de 10 minutes par itération. Motif d'échec rigoureusement contigu :
   24 jugements propres puis 36 échecs d'affilée côté Lucene, 26 puis 34 côté Neo4j —
   70 `INVALID` sur 120.
3. **L'appariement était structurellement impossible.** JMH exécute chaque `@Benchmark` dans son
   propre essai : « Batch judging 60 Lucene + 0 Neo4j », puis l'inverse. Lucene et Neo4j n'ont
   jamais coexisté, et McNemar n'a trouvé aucune paire.

Le run réussissait pourtant sans erreur : `BUILD SUCCESS`, 120 jugements écrits, 20 min 58.
**C'est exactement le genre de résultat qu'il faut savoir jeter.**

Remplacé par `RagQualityEvaluation`, hors de JMH, qui interroge les deux stratégies sur la même
question dans la même itération. Sorties : `rag-quality.jsonl` et `rag-quality-detail.jsonl`.
