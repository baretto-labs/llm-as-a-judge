# WIP — Work In Progress

> Fichier de mémoire de travail. Mis à jour après chaque session de travail.
> Dernière mise à jour : 2026-09-17

---

## Sous-projet `judge-finetune/` — fine-tuning d'un juge Qwen2.5-Coder 14B vs 32B (démarré 2026-09-11)

Tout le détail est dans `judge-finetune/PROTOCOLE.md`.

**Complété**
- **Réorientation du 2026-09-13** : cible unique = exactitude du juge, aucune rétrocompatibilité. Notes graduées et champs hérités (`score`, `rationale`, `suggestsUnknown`, `hintCoverage`) abandonnés, ainsi que `scripts/stats.py` et les dashboards qui les consomment.
- Schéma unifié : system avec marqueur `TÂCHE:`, user en 4 sections (contexte RAG / requête / sortie / critères), assistant `<thinking>` puis `{checks, verdict, reason}` — **contrôles avant verdict**, la génération étant séquentielle, le modèle pose les faits avant de trancher. Verdict PASS ⇔ tous les `checks` à `true`. Les 80 exemples ont été migrés par réécriture de `example()` + `make regen`, sans toucher un seul JSONL.
- **Contrôles variables** : la rubrique s'enrichit d'un contrôle dédié quand la requête porte une contrainte explicite (`signature_conforme`, `format_impose`, `perimetre_respecte`…), pour empêcher le raccourci « marqueur → triplet figé ». 8 rubriques distinctes sur 80 exemples, dont 8 à quatre contrôles répartis 3 PASS / 5 FAIL — les deux polarités sont nécessaires, sinon le raccourci devient « 4ᵉ contrôle ⇒ échec ».
- Trois postures séparées par marqueur de tâche : `CODE_ANALYSIS` (monde ouvert), `RAG_CONTEXT_RELEVANCE`, `RAG_FAITHFULNESS` (monde fermé strict). Cible 200 = 150 / 25 / 25.
- La gravité des cas limites reste gérée par la distinction consigne obligatoire / facultative.
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
2. ~~Générer les 200 exemples~~ : **fait le 2026-09-14, 200/200, 0 erreur de validation**, cibles de **composition** atteintes — 150 `CODE_ANALYSIS` / 25 `RAG_CONTEXT_RELEVANCE` / 25 `RAG_FAITHFULNESS`, 80 `parfait` / 80 `defaillant` / 40 `limite`, 90 `code` / 60 `theorie` / 50 `rag`, 25 verbeux à défaut caché (12,5 %), 105 PASS pour 95 FAIL. Deux réserves issues de l'audit du 2026-09-15 : les verbeux corrects sont **13**, effectif désormais retenu comme cible (la cible initiale de 15 n'avait jamais été réellement atteinte, deux étiquettes étant fausses, et l'atteindre aurait supposé de rembourrer des réponses correctes) ; et si les 9 contrôles **supplémentaires** portent bien chacun les deux polarités, celle des contrôles de **socle** n'avait jamais été vérifiée — `citations_exactes` vaut `true` 25 fois sur 25. **Ces compteurs décrivent la composition, pas ce que le corpus enseigne : voir `judge-finetune/AUDIT.md`.**
3. ~~Produire la matière RAG par extraction réelle~~ : fait. Les 50 contextes RAG viennent d'extractions réelles via `verification/ExtractRagContexts.java` (Lucene `hybrid` et Neo4j `hybrid-graph`, Ollama actif pour les embeddings), conservés tels qu'ils sortent — bruit, doublons, troncatures — et versionnés dans `judge-finetune/verification/contexts/`. **Indexer `OllamAssist/src/main/java`, jamais la racine du dépôt** : elle contient une copie de `llm-as-a-judge` sous `tmp/`, donc le corpus de questions lui-même, ce qui avait produit 100 % de couverture d'indices sur les 30 questions — un artefact. Procédure, pièges et familles : `judge-finetune/data/PLAN_CORPUS.md`.
4. ~~`make split`~~ : refait le 2026-09-15 en `SPLIT_SEED=11`, après le regroupement des familles RAG par contexte (chantier 7). Golden set de 50 — 38 `CODE_ANALYSIS` / 6 `RAG_CONTEXT_RELEVANCE` / 6 `RAG_FAITHFULNESS`, cas 19/21/10, 8 cas verbeux à défaut caché (16 %, plancher du protocole à 10 %), et surtout **zéro fuite de contexte** contre 9 items sur 11 auparavant. La graine 11 a été retenue sur 17 essais, départagée par la couverture de `RAG_FAITHFULNESS` — 6 items contre 4 pour l'ancienne graine 3, devenue caduque avec le changement de structure des familles. La fuite, elle, est nulle pour les 17 graines : le regroupement la rend structurellement impossible. **Attention : dans le `Makefile`, `SEED` désigne la liste des lots JSONL — la graine du tirage est `SPLIT_SEED`.**
5. ~~Reprise ciblée du corpus~~ : **les 8 chantiers de l'audit sont clos.** Les tests de permutation sont tous dans le bruit (`CODE_ANALYSIS` 60,0 % p=0,131 ; `RAG_FAITHFULNESS` 72,0 % p=0,177 ; `RAG_CONTEXT_RELEVANCE` 60,0 % p=0,983). Règle acquise et coûteuse : **tout seuil choisi après coup se compare à un tirage de permutation, jamais à un taux de base** — un écart annoncé à +8,8 σ n'en valait que +1,3. Un **chantier 9** a été ajouté le 2026-09-17, voir ci-dessous.
6. **Journée du 2026-09-17 — quatre acquis.**
   - **Fuite déterministe trouvée et corrigée** : « requête à consigne facultative ⇒ PASS » valait **17/17**. Correctif en 3 lots sans créer ni supprimer d'exemple et sans déplacer un verdict : diversification des formulations (6 tournures), clause ajoutée à 12 FAIL existants, et 3 items où le volet facultatif est réellement **traité** — dont `b10-011` où il est traité **faussement**, défaut imputé à `exactitude_technique` et non à `respect_consignes`. Règle de surface ramenée à **17/30 (57 %)**, et **3/6 (50 %) sur le golden set**.
   - **Chantier 9 d'`AUDIT.md` — l'erreur la plus instructive du projet.** Ce correctif a lui-même créé une fuite **pire** : le script plaçait la clause en paragraphe isolé, les 17 items d'origine la portant en incise. Résultat, « paragraphe isolé ⇒ FAIL » classait **30 items sur 30**, et l'anomalie a traversé une régénération, une validation à 0 erreur, trois mesures et un commit. **C'est le désaccord d'un relecteur humain qui l'a révélée**, à `b08-011`. Leçons : toute correction de biais introduit un stimulus à mesurer comme le biais d'origine ; mesurer la **forme**, pas seulement le fond ; un désaccord d'annotateur constant par ailleurs est un signal sur le corpus avant d'être une erreur de l'annotateur.
   - **`judge-finetune/PREENREGISTREMENT.md` signé et horodaté avant tout entraînement** (2026-09-17T19:42:37+02:00). Fixe le gel du corpus, **une seule** métrique principale (justesse stricte du verdict sur 50 items), la comparaison principale **`14B-finetuned` contre `14B-baseline-conventions`** — et non contre le modèle nu, qui serait un homme de paille —, McNemar apparié + bootstrap, la puissance connue d'avance (~15 points détectables, moins de 10 non concluant), 6 métriques secondaires non promouvables, et l'engagement de publier un résultat défavorable. Addendum daté : les 12 items RAG du golden ne reposent que sur **5 contextes distincts**, donc leur taille d'échantillon effective est plus faible que leur nombre.
   - **Relecture : 21 items sur 50**, accord verdict **20/21**, **κ = 0,901 IC 95 % [0,674 — 1,000]**. Les 4 items à difficulté réelle sont couverts, l'échantillon aléatoire de 8 (graine 17, tiré et commité **avant** relecture) est terminé sans un désaccord de verdict. **Le chiffre à publier en premier n'est pas le κ mais l'accord complet contrôle par contrôle : 16/21 = 76 %.** Ce κ est un **majorant** : les items sont présentés avec leurs affirmations déjà isolées en tableau.
7. **Ordre de reprise, arrêté le 2026-09-17.**
   1. ~~Arbitrage sur `respect_consignes`~~ : **rendu à froid le 2026-09-18 — la convention tient.** Les deux imputations sur `b08-011` et `b04-014` étaient des erreurs d'inattention, non une récusation : une demande facultative ignorée n'entre pas dans `respect_consignes`. **Aucune modification du corpus**, les deux étiquettes sont maintenues et les ~10 réécritures sont épargnées. Les premiers passages restent consignés tels quels — ils comptent pour le κ, fatigue comprise, donc l'accord complet reste **16/21** et l'accord verdict **20/21**. Les trois désaccords de contrôle sur ce point sont **un désaccord unique répété**, à présenter ainsi dans le REX. Premier test réel du protocole à deux colonnes : le passage fatigué nourrit la mesure de reproductibilité, le passage à froid fixe l'étalon.
   2. ~~Instrumentation du coût~~ : **faite le 2026-09-18.** `scripts/train_variant.sh`, câblé sur `make train-14b` / `train-32b`, produit un relevé complet par variante — durée, mémoire de pointe, s/itération, jetons vus, hyperparamètres, versions épinglées, machine. Éprouvé trois fois sur le 0.5B en cache (20 itérations, 12,7 s, 0,65 s/it, pic 3,56 Go, 19 782 jetons). **Trois décisions imposées par les essais, à ne pas défaire :**
      - **Les poids sont récupérés hors du chronomètre.** Le 32B n'est pas en cache et pèse ~18 Go : un téléchargement inclus dans la durée fausserait le chiffre publié. La durée de récupération est relevée à part, et « intégralement en cache » signifie *tous* les fichiers — un cache partiel est fréquent, mlx-lm ne récupérant que ce qu'il lui faut.
      - **Les relevés vont dans `mesures/cout/`, jamais sous `results/`**, qui est dans `.gitignore` et supprimé par `make clean-results`. Sans ce déplacement, les chiffres auraient été mesurés puis perdus — exactement ce que le script existe pour empêcher.
      - **Deux chiffres mémoire, un seul fait foi.** Sur Apple Silicon les allocations Metal n'apparaissent pas dans le RSS : c'est `memoire_pic_go` qu'il faut publier, `memoire_rss_max_go` étant très inférieur et trompeur. Le relevé porte la note.
   3. **Balayage systématique des corrélations de surface**, avant le gel : longueur, placement, ponctuation, nombre de sections, présence de blocs de code. La fuite du jour a été trouvée par accident ; le chantier 9 montre qu'un script ne trouve que ce qu'on pense à lui demander.
   4. Puis gel, puis entraînement. Pendant qu'il tourne : variante `14B-baseline-conventions` dans `configs/variants.json`, McNemar apparié et métriques par strate dans `benchmark_judges.py`.
   5. En parallèle, sans rien bloquer : les 29 items de relecture restants, pour resserrer l'IC du κ d'environ moitié.
8. **Objectif du REX, fixé par l'utilisateur** : partager qu'on peut faire du LLM-as-a-Judge en local, que le fine-tuning n'est pas si coûteux, et qu'il améliore la qualité du juge. **Rien à prouver** : un résultat non concluant sera publié comme tel. Ajout prévu de `gemini-flash` et `gemini-pro` pour permettre un choix éclairé au coût près — d'où une conséquence majeure : **la vérité de référence du golden set doit être humaine**, sinon le benchmark mesure « imiter Claude » et pénalise structurellement un juge extérieur. La distillation reste légitime pour les 150 items d'entraînement.
9. **Fatigue de l'annotateur — arbitrage rendu.** Acceptable pour le κ, qui mesure la reproductibilité du jugement humain et doit l'inclure. **Inacceptable pour l'étalon**, qui doit être juste et non représentatif : une étiquette fausse à 23 h pénalise les modèles qui avaient raison. D'où la discipline : le **premier passage** alimente le κ, l'**arbitrage à froid** fixe l'étiquette — les deux colonnes existent déjà dans `REVUE_GOLDEN.md`. Heure et rang dans la séance à consigner désormais, pour tester l'effet à 50 items. Sur 21 items et 4 désaccords, aucune conclusion n'est tirée : ce serait refaire l'erreur des +8,8 σ.
7. `make train-14b`, `make train-32b`, puis le benchmark. Le 14B a été sondé sur 20 itérations : ~11 s/itération, pic 11,08 Go, soit ~1 h 15 pour 400 itérations.
8. Mesurer la faisabilité du QLoRA 32B sur 36 Go (repli : `NUM_LAYERS=8`, puis `MAXLEN=1024`). Attention, l'audit signale que `MAXLEN=1024` tronquerait une fraction non négligeable des exemples (p50 = 940, p90 = 1116 tokens) — contrairement à 2048, où aucun des 200 ne dépasse.

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
