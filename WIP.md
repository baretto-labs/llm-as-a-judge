# WIP — Work In Progress

> Mémoire de travail. Mise à jour après chaque session.
> Dernière mise à jour : 2026-10-20
>
> **L'historique détaillé n'est plus ici.** Il vit dans les documents qui font foi :
> `judge-finetune/REX_TRAME.md` (tous les chiffres), `AUDIT.md` (les défauts du corpus),
> `PREENREGISTREMENT.md` et `PREENREGISTREMENT_RELECTURE2.md` (ce qui a été déclaré avant mesure),
> `data/REVUE_GOLDEN.md` (la relecture), `PROTOCOLE.md` (la méthode), `TRIAGE_POSTHOC.md`.

---

## Où on en est

Benchmark RAG (Lucene vs GraphRAG-Neo4j) jugé par un LLM entraîné et servi en local.
**Le code n'est plus tout à fait figé** : la sortie structurée a été ajoutée aux deux juges
de campagne le 2026-10-18, derrière un drapeau par défaut inactif. Hors de ce chantier, tout
le travail restant est éditorial.

**Branche active** : `talk/v1`
**Objectif** : l'exposé de **novembre 2026 — DevFest Paris, 20 min, ~400 personnes**.

### Chemin critique — ces trois tâches seules décident si l'exposé existe

1. **Reformuler** les 23 diapositives sur 31 encore écrites dans les mots de l'assistant.
2. **Couper** ~12 minutes : le support fait ~32 min de script pour un créneau de 20.
3. **Dessiner** les dix états du schéma de construction du juge (échafaudage ASCII en place dans
   `demo/CONFERENCE-V2.md`, versions longues dans `demo/SCHEMA-ETATS.md`).

Tout le reste améliore sans être indispensable.

### Tombé le 2026-10-17 à 14 h 27 — la quatrième ligne existe

**`32B-baseline-conventions`**, 150/150 générations. Même invite, mêmes conventions, mêmes 50 items,
3 passes : **seule la taille change**. Paire pré-déclarée dans `configs/variants.json`
(« effet de la taille, à conventions identiques »). ~80 s par génération mesurées (et non 65 estimées), 150 générations, ≈ **3 h 10**.
But : donner une **quatrième ligne** au tableau des variantes de la diapositive 21.

Lecture fixée avant le résultat, et **appliquée telle quelle** :

| le 32B rend | conclusion | ce qui est sorti |
|---|---|---|
| **~76 %** | trois tailles au même chiffre ⇒ c'est l'étalon qui plafonne | non |
| **hors [61 %, 91 %]** | résultat détectable, rapporté avec son intervalle | non |
| **entre les deux** | **non concluant**, et c'est le mot qui sera employé | **← 90 %** |

```
  justesse stricte (vote majoritaire)   90 %   contre 76 %
  accord κ moyen                        0,80   contre 0,48   IC95 [0,64 ; 0,93]
  stabilité du verdict                  92 %   contre 76 %
  format strict (« schéma »)             0 %   contre 0 %

  Δ justesse apparié = +14,0 points, IC95 bootstrap [+2,0 ; +26,0],
  McNemar p = 0,0654, 11 paires discordantes.   (produit par le harnais,
  paire pré-déclarée — aucun calcul écrit après coup)
```

**Non concluant**, et c'est le mot employé. ⚠️ **Ne pas plaider** que l'IC95 exclut zéro : McNemar ne
rejette pas, et la bande était écrite avant. À un item près — 92 % — le résultat sortait de la bande.
C'est un fait à dire si on insiste, pas un argument pour déplacer la conclusion.

**Ce que ce chiffre tue quand même : l'hypothèse de plafond.** Le corpus ne plafonne pas à 76 %,
puisqu'un modèle plus gros atteint 90 % sur le **même** corpus avec la **même** invite. L'écart n'est
pas déclarable à n = 50 **et** le plafond n'est plus défendable — les deux tiennent ensemble, et c'est
le propos.

**Appliqué au support, en un passage** (`CONFERENCE-V2.md`, HTML régénéré, 31 sections) :
- diapositive 21, à l'écran : quatrième ligne `| + un modèle 32B | 90 % | 0,80 | 92 % | 0 % |` ;
- **trois affirmations devenaient fausses, corrigées** : « achètent **toute** la justesse » → « l'essentiel
  de » (76 sur 90) ; « aucun des **deux** leviers n'a amélioré cette colonne » → « ni les conventions ni
  l'entraînement », puisqu'un troisième l'a améliorée (κ 0,80) ; le script disait « les **trois** versions »
  et « la justesse ne bouge plus **après la deuxième ligne** » ;
- **une réponse préparée fausse, refaite** — la question hostile « pourquoi pas un plus gros modèle ? »
  répondait « 76,0 % contre 76,0 %, p = 1,0000 », qui mesure **l'entraînement**, et concluait « le plafond
  n'est pas la taille du modèle ». Deux questions, une seule mesure, et une conclusion que le banc
  contredit. C'est la **huitième** affirmation fausse retirée, et la première qui n'était pas à l'écran
  mais dans une réponse qu'on aurait prononcée devant 400 personnes ;
- la piste n° 4 de la liste des leviers portait la même faute, corrigée ;
- **la ligne « plus gros modèle » de la diapositive 29 ne revient pas** : elle ne devait revenir que sur
  un résultat détectable. Règle pré-déclarée, appliquée.

⚠️ **La seule chose à vérifier à l'œil** : la diapositive 21 était déjà la plus chargée et passe à
**cinq lignes de tableau**. Si ça débord, `<!-- _class: dense -->` est le remède déjà utilisé sur deux
autres diapositives. Je ne l'ai pas appliqué : c'est un choix visuel.

**Le dépouillement est déjà écrit et éprouvé**, pour que l'application de la grille ne soit pas
rédigée une fois les chiffres connus :

- `scratchpad/quatrieme_ligne.py` — importe `majority_verdicts` et `strict_accuracy` du harnais
  lui-même, refuse de dépouiller une variante dont les 150 générations ne sont pas en cache, et
  **se contrôle d'abord sur le 14B** : à blanc, il a reproduit mot pour mot la troisième ligne déjà
  publiée sur la diapositive 21 — `76 % | 0,44 | 58 % | 100 %`. Il sort la ligne à coller et
  applique la grille ci-dessus, sans tolérance inventée (« au même chiffre » = le même chiffre).
- `scratchpad/rapport_complet.sh` — reconstruit `results/report.md` et `metrics.json` sur toutes
  les variantes complètes. **Nécessaire** : `bench_variant.sh` passe `--variants <une seule>` et
  `benchmark_judges.py` ne sérialise que les variantes sélectionnées, donc chaque banc **écrase**
  le rapport des précédents — et `results/` est dans `.gitignore`, il n'y avait aucun filet.
  La reconstruction ne relance aucune génération (`--report-only` ne lit que `runs/`) et sa fidélité
  est prouvée : le rapport reconstruit est **identique octet pour octet** à la sauvegarde.
  Sauvegarde des trois variantes : `scratchpad/backup-results-3variantes/`.

C'est aussi le moyen d'obtenir le Δ, l'IC95 et le McNemar de la paire 14B↔32B : la comparaison est
**déclarée dans `configs/variants.json`**, donc c'est le harnais qui les produit, pas un calcul écrit
après coup.

`train-32b` reste **non lancé** et sa faisabilité QLoRA sur 36 Go reste ouverte. Volontaire : servir
n'est pas entraîner, et la variante fine-tunée mélangerait taille et entraînement.

### Terminé — Mistral, lancé à 14 h 27, rendu à 15 h 44

La chaîne a franchi son portail : **3 fichiers `.safetensors`, 12 663 Mo** vérifiés avant lancement,
pas seulement un processus terminé. `Mistral-24B-baseline-conventions` tourne. Lecture déjà fixée dans
`PREENREGISTREMENT_JURY.md`, écrite avant toute génération : 8 items cibles, n = 8, jamais de
pourcentage, bandes ≥ 6/8 · 4–5 · ≤ 3/8.

**Avancement au 2026-10-17 à 20 h 05 : 29 générations sur 150**, soit ~36 s par génération et une
fin attendue vers **21 h 20**. Un `caffeinate -i -w` est attaché au PID du banc lui-même, pas à un
processus plus court. La suite est **déjà enchaînée et n'attend personne** : à l'extinction du banc,
reconstruction du rapport multi-variantes (`--report-only`, aucune génération — elle répare l'écrasement
de `metrics.json` par les passes mono-variante), puis dépouillement.

**Le dépouillement est écrit et éprouvé AVANT le chiffre**, c'est tout son intérêt. Il importe
l'extraction de verdict du harnais — aucune seconde logique de lecture ne peut diverger — et il
s'arrête sans rien conclure si ses témoins ne retombent pas. À l'essai à blanc ce soir, ils retombent :
les effectifs de `TRIAGE_POSTHOC.md` sont reproduits à l'identique sur les deux variantes
(38/30/8 · 12/8/4 et 29/24/5 · 21/14/7), et surtout **les deux listes gelées d'items sont bien
exactement ce que disent les données** — les 8 systématiquement faux du juge et les 5 de la variante
fine-tunée. La grille ne peut donc plus être réécrite après coup.

**LE RÉSULTAT, lecture appliquée sans renégociation : 2 sur 8.** Bande ≤ 3/8, dont la conclusion
était écrite d'avance — « le jury ne fait pas mieux qu'un entraînement de plus », qui en corrigeait 3.
Consigné dans `judge-finetune/JURY_RESULTAT.md`. **Le jury ne peut donc plus être la suite annoncée**,
et la diapositive 29 a été réécrite en conséquence (voir plus bas).

Ce que la mesure a sorti de plus fort que le plan qu'elle a tué : **7 des 8 items sont étalon FAIL /
juge PASS** — le juge n'erre pas au hasard sur ses erreurs systématiques, il est **trop indulgent** —
et **Mistral partage cette indulgence sur 6 d'entre eux**. Deux familles sans ancêtre commun, le même
biais de complaisance, sur les mêmes copies.

Post hoc, et sans pouvoir de décision : sur ces mêmes 8 items, le jury corrige 2, l'entraînement 3,
la taille 5. **Trois items résistent aux quatre configurations** — `b04-002`, `b06-008`, `b07-002`.

### Le dispositif de la file — lancé le 2026-10-17 à 11 h 56

Le Mac est tenu éveillé par `caffeinate -i -w <pid de la chaîne>` : il **survit à la fin du 32B**,
contrairement au premier `caffeinate` qui surveillait le banc lui-même et serait mort avec lui.
⚠️ **Rabattre l'écran endort la machine quand même** et tue tout : l'écran reste ouvert.

Script : `scratchpad/chaine.sh`. Journal horodaté append-only : `scratchpad/chaine.log`.

1. attend la fin du banc 32B ;
2. attend la fin du téléchargement Mistral (13 Go, lancé en parallèle car il ne coûte ni RAM ni GPU)
   et **vérifie des poids présents** — pas seulement un processus terminé. Téléchargement incomplet
   ⇒ la chaîne s'arrête et ne lance pas le banc ;
3. lance `Mistral-24B-baseline-conventions`.

Lecture **déjà fixée** dans `judge-finetune/PREENREGISTREMENT_JURY.md`, écrite avant toute
génération : 8 items cibles, n = 8, jamais de pourcentage, bandes ≥6/8 · 4–5 · ≤3/8.

### Mort-né — le re-jugement RAG hors-ligne est impossible

Objectif visé : rejuger les 240 contextes stockés avec le juge **à conventions**, pour savoir si les
chiffres du titre (48,3 % Lucene / 23,7 % Neo4j) tiennent quand le juge change. Le contrôle de
lecture passait sur les quatre cellules publiées.

**Bloqué par `RetrievalBenchmark.java:447-449`.** Le champ `generated` du journal est un champ
d'**affichage** : ordre **non mélangé** et troncature à **3000** caractères, là où le juge recevait
l'ordre mélangé par `question.hashCode()` tronqué à **6000**. Le prompt réellement jugé n'est donc
pas reconstituable depuis le disque.

Et la perte est **asymétrique**, ce qui achève la piste :

| stratégie | contextes amputés | reproductibles |
|---|---|---|
| lucene | **118 / 120 (98 %)** | **2** |
| neo4j | 4 / 120 (3 %) | 116 |

Rejuger ne comparerait plus que **2 items Lucene contre 116 Neo4j**. Ce n'est pas un biais à
déclarer, c'est l'absence de matériel. Pour obtenir ce chiffre il faut **rejouer la récupération**
(Java + Lucene + Neo4j), et au passage stocker le prompt réellement envoyé. Non lançable sans
surveillance, et hors du chemin critique.

**Au passage, un fait mesuré et utilisable** : Lucene rend des contextes systématiquement plus longs
que Neo4j — 98 % dépassent 3000 caractères contre 3 %. Du bruit, pas de la couverture.

**Levé le 2026-10-18, pour la campagne à venir et non pour celle du 2026-09-24.** Les 240 contextes
de septembre restent irrécupérables : rien ne les répare. Mais la prescription de ce paragraphe —
« rejouer la récupération et au passage stocker le prompt réellement envoyé » — est exactement ce
que fait `RagCampaignGenerate` : contexte **entier, extrait par extrait, jamais tronqué**, plus la
chaîne exacte soumise au générateur. Rejuger hors-ligne est désormais possible **sur les nouvelles
générations**, et c'est ce qui rend le second juge abordable.

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
| **Le support raconte le juge À CONVENTIONS, de bout en bout** | Arbitré le 2026-10-17, annulant celui du 2026-10-14 qui disait l'inverse. Motif : les diapositives 22 et 29 se contredisaient sur la même quantité, et la mesure montre que le motif d'origine ne coûte presque rien — aucun chiffre d'indulgence ne bouge de plus de 4 points. κ 0,48 et stabilité 76 % sont désormais les chiffres de référence |

---

## Questions ouvertes

- **Métrique « format normalisé » jamais produite** — l'amendement du 2026-09-19 la déclare, le
  Makefile prévient que sans `BENCH_ARGS=--format-normalise` elle ne sort d'aucune commande, et
  constat du 2026-10-17 : **aucune variante ne l'a**. `results/runs/` ne contient aucune entrée
  suffixée, `report.md` n'en parle pas. Les quatre variantes sont donc comparables entre elles, mais
  une mesure déclarée reste sans données. À savoir avant les questions de la salle.
- **Une phrase manque à « Le résultat », et c'est tout ce qui reste de l'arbitrage.** Le banc RAG a
  tourné avec le juge **fine-tuné** au checkpoint 200 (`REX_TRAME.md` l.110), et le support ne le dit
  nulle part à l'écran. Le gage existe déjà dans le tableau de la 21 : **76 % contre 76 %,
  p = 1,0000** — les deux juges sont indiscernables en justesse. Formulation proposée dans les notes
  de la 14, à valider. Alternative écartée : rejouer le banc RAG avec le juge à conventions, deux
  heures de machine, et ça redéfinirait les chiffres du titre.
- **Accord par contrôle : disponible pour le fine-tuné seulement.** Désormais ce n'est plus le juge
  décrit à l'écran. Noté dans les notes de la 21 ; à ne pas présenter comme celui du juge raconté.
- **Réparer le test de verbosité** — `AUDIT.md` §2 : les deux groupes ne se chevauchent pas en longueur,
  et sur 40 familles du golden **3 seulement** portent les deux longueurs, donc l'appariement que la
  diapositive annonce n'existe pas. Correctif : jeu dédié `data/verbosity/`, **hors du tirage** — sinon
  `make split` redessine le golden set et change les 50 items du second relecteur en cours de route.
  Design apparié, 10 cas de base rendus en version bavarde et concise, McNemar sur les paires. Bonus.
- **Bug latent** — le preset `hybrid-graph-hyde` pose `hydeEnabled=true` et `rerankingEnabled=false`, or
  `Neo4jGraphRagStrategy.java:246` ne branche le modèle HyDE que si le reranking est actif. Ce preset
  tournerait **sans HyDE** en annonçant son nom. Jamais publié, donc rien d'invalidé.
- **Abandonné pour l'exposé, versé à l'article de blog** : `citations_exactes` dégénéré (vrai 25 fois
  sur 25).
- **Jury multi-modèles : décision réouverte sciemment le 2026-10-17.** Il avait été écarté comme
  sous-dimensionné — il faudrait rattraper 10 des 12 désaccords pour conclure. **La question a
  changé** : il ne s'agit plus de montrer qu'un jury juge mieux, hors de portée à n = 50, mais de
  vérifier la **condition d'existence** du levier sur 8 items nommés. Déclaré avant toute génération
  dans `PREENREGISTREMENT_JURY.md`. Motif : c'est la dernière affirmation non mesurée de l'écran.

---

## Plan arrêté le 2026-10-18 — la sortie structurée du juge

**Constat, vérifié et non déduit.** Aucun juge du dépôt n'utilise la sortie structurée.
`RagContextJudge` et `RagAnswerJudge` appellent `model.chat(...)` en brut — jamais `AiServices`,
donc aucun schéma n'est généré implicitement. Trois regex extraient le verdict
(`RagContextJudge:141-143`) ; toute sortie inanalysable vaut `INVALID`, jamais PASS.

**Le commentaire `RagContextJudge:40-44` est faux tel qu'il est écrit.** Il justifie l'absence de
schéma par le bloc `<thinking>` qui précède le JSON — « la sortie structurée de LangChain4j exige
un JSON seul et échouerait ». Lu dans les jars : `OllamaChatRequest` porte `setFormat(Object)`
**et** `setThink(Boolean)`, et le builder expose `.responseFormat(...)`, `.think(true)`,
`.returnThinking(true)`. Raisonnement et schéma sont orthogonaux. La contrainte réelle est celle
d'un seul serveur : **`mlx_lm.server` 0.31.3 n'implémente pas `response_format`** — aucune
occurrence dans `server.py`, aucun décodage sous grammaire, champ **ignoré en silence**. Ollama
0.40.6 accepte un schéma complet. À corriger dans la javadoc, hors campagne.

**Ce que ça reclasse.** Repassé dans le parseur du dépôt, `14B-baseline-nu` rend **150/150
INVALID**, et **rien n'est tronqué** (budget 1024 jetons, plus longue sortie 831). L'invite nue
n'est pas un juge qui juge mal : c'est un juge qui ne rend jamais le format — il raisonne, il
emploie les bons noms de contrôles, il s'arrête avant le JSON. Le levier derrière le **0 % → 76 %**
est donc « écrire le format attendu », pas « écrire des règles de jugement ». INVALID ailleurs :
`32B-baseline-conventions` 0, `14B-finetuned` 0, `Mistral-24B` 10/150 (6,7 %),
`14B-baseline-conventions-fewshot` 3 — plus 3 erreurs HTTP, d'où ses 153 lignes.

**L'ordre, révisé le 2026-10-18 à la demande de l'utilisateur.** Le plan initial faisait
juger les deux juges MLX d'abord et le juge à schéma ensuite. La consigne était l'inverse :
dès que les 180 réponses existent, **contraindre le schéma puis lancer les bancs**. Le juge
à schéma passe donc en premier. Les juges MLX, eux, ne peuvent pas porter de schéma et sont
inchangés — l'ordre entre eux et le juge à schéma ne change aucun verdict, chaque juge relisant
les **mêmes 180 réponses figées**.

1. la campagne à trois bras produit ses 180 réponses — **fait, 180/180, zéro échec** ;
2. le **juge à schéma** servi par Ollama rejuge ces mêmes 180 réponses ;
3. les **deux juges MLX déjà déclarés** suivent — Qwen2.5-Coder-32B, puis gemma-4-26b-a4b ;
4. aucune régénération à aucune étape ;
5. paire de comparaison et lecture **fixées au pré-enregistrement avant la première génération**.

Ce juge est une **comparaison supplémentaire**, jamais un remplacement rétroactif des deux autres.
Arbitrage restant, mesurable et non mesuré : contraindre le décodage change ce que le modèle
produit — le raisonnement devient une valeur de chaîne échappée.

## Fait le 2026-10-18

- **La campagne à trois bras a produit ses 180 réponses** : `vector` 60, `vector-bm25` 60,
  `graphrag` 60, **zéro échec**, dans `benchmarks/rag-campaign.jsonl`. Générateur `qwen3.8:27b`
  via Ollama, un index par bras dans son propre répertoire temporaire.
- **La sortie structurée est en place dans les deux juges de campagne.** `RagContextJudge` et
  `RagAnswerJudge` exposent un `ResponseFormat` à schéma JSON (`checks` avant `verdict`, les trois
  contrôles requis, `additionalProperties: false`), derrière `-Djmh.judge.schema` et
  `-Djmh.answerjudge.schema`, **défaut `false`** : le comportement publié ne bouge pas. Activer le
  drapeau avec le fournisseur `openai`/MLX **lève une erreur franche** plutôt que de produire un
  run qui se croit contraint — `mlx_lm.server` ignore le champ en silence. La javadoc
  `RagContextJudge:40-44` ne justifie plus l'absence de schéma par une raison fausse : la phrase y
  est **citée puis réfutée**, datée.
- **`think` a dû être retiré, et la divergence est déclarée.** Le dispositif gelé prévoyait
  `think(true)` pour que le raisonnement parte dans le champ natif d'Ollama. Sonde de 2 items :
  Ollama refuse l'appel — `{"error":"\"qwen2.5-coder:32b\" does not support thinking"}`. Le
  pré-enregistrement avait fixé la conduite pour ce cas exact — déclarer la divergence, surtout
  pas ajouter un champ `thinking` au schéma après coup. Appliquée telle quelle, amendement daté
  en fin de `benchmarks/PREENREGISTREMENT_SCHEMA.md`.
  **Conséquence à ne pas enjoliver** : sous schéma contraint le juge **ne raisonne pas** — le
  décodage ne peut émettre que le JSON. C'est un **quatrième confondu**, le plus lourd, et il joue
  *contre* le juge à schéma. Le taux d'INVALID reste lisible (propriété de forme) ; **aucun chiffre
  d'accord issu de ce dispositif ne va à l'écran**.
- **Ce que la sonde a évité.** Deux items ont suffi à attraper le blocage : sans elle, 360
  jugements revenaient tous INVALID pour cause d'appel en échec, et le résultat se serait lu comme
  « le schéma ne tient pas ».
- **Le run MLX lancé avant le patch a été arrêté à 14/180 et supprimé.** Il jugeait sans schéma,
  dans le mauvais ordre. Il avait déjà relevé **5 INVALID sur 28 jugements** chez un 32B *avec*
  conventions — à comparer aux 0 du banc golden set. Chiffre non publiable (n = 28, run interrompu),
  noté ici parce qu'il a motivé l'intérêt porté au taux d'INVALID.


- **La boucle du banc RAG est scindée en deux.** `RagQualityEvaluation` générait et jugeait dans la
  même itération, deux bras, un juge. Deux classes la remplacent pour la campagne du talk :
  `RagCampaignGenerate` (récupère, répond, persiste — aucun juge) et `RagCampaignJudge` (relit,
  juge, écrit un fichier par étiquette de juge — aucune génération). Raison mesurée : 18 Go de
  générateur plus 18,4 Go de juge ne tiennent pas résidents sous ~27 Go, et un second juge ne doit
  pas re-payer 180 générations. `RagQualityEvaluation` n'est pas touché : les chiffres publiés
  restent lisibles tels quels.
- **Trois bras indépendants, un index chacun** : `vector` (Lucene `knn-only`), `vector-bm25`
  (Lucene `hybrid`), `graphrag` (Neo4j `hybrid-graph`). **Le graphrag n'est donc plus mesuré deux
  fois** — l'ancien protocole le passait dans deux exécutions appariées. La stabilité gratuite que
  ce doublon offrait est remplacée par le second juge, qui mesure mieux la même chose.
- **Générateur : `llama3.1:latest` (4,9 Go) → `qwen3.8:27b` (18 Go), raisonnement actif.** Sondé
  avant de dépenser : **73 s par génération**, soit ~3 h 45 pour les 180. Ollama range le
  raisonnement dans un champ séparé — **aucune fuite de `<think>`** dans la réponse persistée,
  vérifié sur la ligne de sonde.
- **La disjonction de famille générateur/juge est abandonnée, et déclarée comme telle.**
  `qwen3.8:27b` partage sa famille avec le premier juge (`Qwen2.5-Coder-32B`). La javadoc de
  `RagAnswerer` affirmait que la disjonction était « une condition de validité » : la phrase est
  réécrite, pas laissée fausse. Ce qui la remplace : **le second juge est un Gemma, disjoint du
  générateur**. Si les deux juges classent les trois bras dans le même ordre, la parenté n'a pas
  porté le résultat ; s'ils divergent, aucun classement ne va à l'écran et c'est le désaccord qui
  se raconte. Aucun troisième juge ne départagera — il n'y a pas de référence contre quoi départager.
- **`PREENREGISTREMENT_REPONSE.md` amendé avant la moindre génération.** Preuve positive à
  l'instant de l'écriture : `rag-quality-detail.jsonl` = 240 lignes, **0** en `binaire-v2`, et
  aucun fichier `benchmarks/rag-campaign*`.
- **Écrit avant de lancer, pour qu'aucune diapo ne le lise à l'envers : l'accord entre les deux
  juges n'est pas une justesse.** Les réponses de la campagne RAG n'ont aucune étiquette de
  référence. Le seul endroit du dépôt où un juge peut être dit faux reste l'étalon
  `judge-finetune/data/golden/test.jsonl`. Un désaccord dira que les deux juges divergent, jamais
  lequel a raison.
- **Génération lancée**, 180 réponses. Les deux passes de juge suivent, l'une après l'autre.

---

## Fait le 2026-10-17

- **Le banc few-shot a rendu : κ = 0,348, IC95 [0,17 ; 0,53] → « NON CONCLUANT ».** C'est la
  bande du milieu de `PREENREGISTREMENT_FEWSHOT.md` (0,29–0,66), déclarée la plus probable à
  n = 50 et **acceptée d'avance**. Le mot qui va à l'écran est « non concluant », pas
  l'estimation ponctuelle — la référence des conventions, κ = 0,479 IC95 [0,29 ; 0,66], est
  dans l'intervalle. Les 150 générations sont passées sans arrêt anticipé ni examen
  intermédiaire, et **aucun second jeu d'exemples ne sera tiré** : les six identifiants étaient
  gelés.
  Secondaires, descriptives : **3 des 8 erreurs systématiques corrigées** (`b03-005`, `b09-014`,
  `b12-011`) — exactement le même décompte que l'entraînement — mais **8 erreurs nouvelles
  introduites**, soit un solde nul. Justesse majoritaire 0,68 contre 0,76 ; stabilité 82 %
  contre 76 % ; **415 jetons de complétion contre 237**, ce qui confirme la sonde. Le portail
  du harnais affiche « non recevable », mais son contrôle de format strict ne vaut rien ici :
  `bench-fewshot` tourne délibérément sans `--format-normalise`.
  **Ce que ça arme à l'oral** : « le levier que la littérature désigne comme principal, je ne
  l'avais pas essayé — je l'ai essayé, mon banc ne sait pas trancher à cette taille. »

- **Le juge du banc RAG passe à Qwen2.5-Coder-32B, et c'est une correction d'un choix fait trois
  heures plus tôt le même soir.** `RagContextJudge` et `RagAnswerJudge` étaient réglés sur
  `Mistral-24B` (port 8085) sur un **argument** : famille disjointe du générateur Qwen, donc pas
  de biais d'auto-préférence. Le rapport multi-variantes reconstruit dans la foulée le contredit
  par une **mesure** : Mistral-24B accorde κ = 0,349 avec l'étalon, le 32B **κ = 0,801**
  (justesse 90 %, stabilité 92 %, et 0,97 de justesse moyenne sur les trois contrôles de
  fidélité — ceux-là mêmes qu'applique le juge de réponse). Un risque contre un défaut constaté :
  on prend le meilleur juge mesuré. **La contrainte de disjonction est déplacée sur le
  générateur**, qui est une constante identique sur les trois bras : `RagAnswerer` passe de
  `qwen2.5:7b` à `llama3.1:latest` (4,9 Go, déjà en cache). Les deux arguments sont préservés.
  `benchmarks/PREENREGISTREMENT_REPONSE.md` porte l'amendement daté, **légitime parce qu'aucune
  génération n'a eu lieu** : preuve positive relevée au moment de l'écrire — 240 lignes dans
  `rag-quality-detail.jsonl`, **0** en `binaire-v2`, **0** portant un champ `answer`.
  **Reste à sonder avant de lancer** : 18,4 Go + ~5 Go résidents contre la limite *wired* de
  ~27 Go qui a déjà provoqué un OOM Metal ce soir. À mesurer, jamais à supposer.

- **Le plan de l'exposé est arrêté et écrit : `demo/PLAN-DEVFEST-2026.md`.** 13 diapositives,
  **16 min 55**, avec une **réserve de coupe déclarée d'avance** (cinq coupes, une minute, aucune
  ne touche aux diapos 4, 6, 9, 10, 11, 12, 14). Le plan ajoute une **diapositive 11 neuve** —
  trois biais RAG constatés sur les runs — qui comble le seul trou unanimement relevé par les
  trois agents d'évaluation : l'abstract promet « quelques biais des systèmes RAG » et le plan
  précédent y consacrait une demi-phrase. La diapo 9 (« juger le juge ») redescend de 3:00 à
  **1:30** : j'avais eu tort de la monter, je la jugeais sur sa valeur intrinsèque et non sur ce
  que l'abstract paie.

- **Les trois biais sont tirés des 240 jugements du 2026-09-24, pas de la littérature.**
  (1) ce n'est pas le bruit mais le manque — `bruit_maitrise` est le contrôle qui échoue le moins,
  27 % pour les deux stratégies, contre 43 % et 67 % pour `contexte_suffisant` ; (2) le graphe
  ramène la structure et pas le corps — 22 % de Neo4j *pertinent mais insuffisant* contre 7 % pour
  Lucene ; (3) l'angle mort est le cross-module, 10 % Neo4j contre 50 % Lucene, précisément là où
  j'attendais le gain du GraphRAG. **Les biais 2 et 3 partagent une racine unique** (des nœuds sans
  corps de méthode) qui est probablement mon code de projection : c'est la phrase qui relie les
  diapos 10 et 11, et elle vaut mieux que les trois biais séparés.

- **L'évaluation de la réponse est implémentée.** Jusqu'ici le banc ne jugeait que le contexte :
  aucune réponse n'était générée nulle part dans le dépôt, et le champ `generated` du détail
  contenait **les extraits Java retournés par le moteur** — origine probable de l'erreur
  « réponses justes » du support. Trois fichiers neufs, un modifié :
  - `RagAnswerer` — génère la réponse avec **l'invite du produit** (`RagService.buildPrompt`,
    rendue `public static` pour ça : une copie de l'invite dériverait en silence) et **Ollama
    `qwen2.5:7b`**, T = 0 ;
  - `RagAnswerJudge` — marqueur `RAG_FAITHFULNESS`, contrat d'invite et intitulés des trois
    contrôles **repris mot pour mot** de l'item `b14-011` du corpus, pas inventés ;
  - `RagQualityLigneTest` — 3 tests, sans appel de modèle, qui prouvent que les lignes JSONL sont
    du JSON valide dans les deux régimes. Ces lignes sortent d'un `String.format` à plus de vingt
    arguments et l'erreur d'arité ne se manifeste qu'**après** la boucle de génération : sur un
    banc de deux heures, elle coûterait la campagne.
  - `RagQualityEvaluation` — schéma **`binaire-v2`** : `generated` devient `context`, les champs
    `answer*` apparaissent, McNemar est paramétré pour servir les deux verdicts, et le résumé
    imprime le croisement qui porte la thèse (contexte FAIL → réponse fidèle *contre* infidèle).

- **Deux défauts du juge corrigés, avec leurs raisons.** Le défaut par défaut de `RagContextJudge`
  était `adapters/14b-judge-ckpt200`, c'est-à-dire **le juge fine-tuné — la pire variante
  mesurée** (κ 0,44 contre 0,48 pour les conventions seules, stabilité 58 % contre 76 %). La
  campagne du 2026-09-24 a donc été jugée par elle. Désormais : **aucun adaptateur**, **Mistral-24B**
  au lieu de Qwen-14B, et **les conventions en suffixe système** (`jmh.judge.suffix`, le levier que
  le banc mesure à κ 0,00 → 0,48). Mistral et non Qwen parce que le **générateur** tourne sous Qwen :
  un juge de la même famille que le générateur surnote — biais d'auto-préférence, qui est aussi un
  des biais présentés à l'oral.

- **`benchmarks/PREENREGISTREMENT_REPONSE.md`, écrit avant la moindre génération.** Preuve positive
  à l'écriture : `rag-quality-detail.jsonl` ne porte que `"schema":"binaire-v1"` et zéro champ
  `answer`. Il déclare les **trois bras** — `knn-only` (vectoriel), `hybrid` (vectoriel + BM25),
  `hybrid-graph` (graphrag) —, les **paires de comparaison avant exécution** (principale :
  vectoriel contre vectoriel + BM25, le chiffre que la diapo 12 affirme sans l'avoir), la lecture
  fixée d'avance, et le fait que **le bras graphrag est mesuré deux fois sur les mêmes 60 questions**
  — ce sont 60 observations, jamais 120. Il interdit explicitement toute comparaison avec la
  campagne du 2026-09-24 : le juge a changé de modèle, perdu son adaptateur et gagné les
  conventions, les deux campagnes ne sont pas commensurables.
  ⚠ **Le coût n'est pas estimé, il reste à sonder** : trois appels de chaque sorte avant de lancer
  les 720. La sonde du few-shot avait fait passer un budget de 54 min à 2 h 30.

- **La 4ᵉ ligne du tableau de la diapositive 21 n'est plus en gras, et une phrase fausse est corrigée.**
  Sous une légende « ce que chaque version achète », les trois cellules grasses de `+ un modèle 32B`
  (90 %, 0,80, 92 %) se lisaient comme un classement — exactement ce que la note de la diapositive
  interdit de dire (« NE PAS DIRE : la taille améliore la justesse »). Dégraissées, sauf **κ 0,80**
  qui reste la seule cellule désamorçant le piège κ. Ajouté en `.ref` ce que la note dit déjà :
  « contrôle de plafond, pas comparaison de justesse — 38 copies justes sur 50 contre 45 ».
  ⚠ **La proposition de l'audit d'afficher « non concluant » a été écartée**, et c'est volontaire : la
  note tranche depuis le 2026-10-17 que la 4ᵉ ligne est un **contre-exemple d'existence** contre
  « le corpus plafonne à 76 % », qu'on ne teste pas l'existence et que le script ne prononce donc ni
  valeur-p ni « non concluant ». Décision antérieure, mieux argumentée, conservée.
  Trouvé au passage et corrigé : l'écran affirmait « **Ni les conventions ni l'entraînement** n'ont
  amélioré cette colonne » alors que le tableau juste au-dessus montre l'accord passer de **0,00 à
  0,48** avec les conventions. Devenu « Entraîner n'a pas amélioré cette colonne », qui est vrai
  (0,48 → 0,44). 31,2 min inchangés, 0 diapositive sur 31 ne touche le bord bas.

- **« Sur soixante, le bruit se moyenne » était contredit par la diapositive 22 ; remplacé par l'argument apparié.**
  La diapositive 21 justifiait la confiance par une moyenne ; quatre diapositives plus loin le support
  démontre que **8 erreurs sur 12 sont rendues trois fois identiques**, parce que rejouer le même
  modèle fait varier l'échantillonnage et jamais la compréhension. Un biais systématique ne se
  moyenne pas : il traverse intégralement le 48 % et le 24 %. L'écran dit désormais « sur une copie,
  je ne distingue pas son jugement de son tirage ; ce qui conclut, c'est l'écart entre deux moteurs
  jugés par le même juge ». Deux défauts accessoires réglés au passage : « soixante » désignait le
  banc alors que la ligne mesure l'étalon de 50, et le mot fautif était *bruit*, pas l'usage. Payé en
  supprimant « c'est la troisième ligne qui a tourné sur le banc », redite trois diapositives plus
  loin au meilleur endroit, juste à côté des chiffres : **4374 → 4369 mots**, cinq de gagnés. Re-mesure
  du rendu après coup : 0 diapositive sur 31 ne touche le bord bas.

- **Le juge est validé sur une tâche, et il a tourné sur une autre : la question est désormais armée.**
  Recompté sur `judge-finetune/data/golden/test.jsonl` (champ `meta.task`, pas `meta.marker`) :
  **38 CODE_ANALYSIS, 6 RAG_CONTEXT_RELEVANCE, 6 RAG_FAITHFULNESS**. Or le banc RAG tourne à 100 %
  sur `RAG_CONTEXT_RELEVANCE` — `RagContextJudge.java:35-38` l'écrit noir sur blanc, « les 6 items du
  golden set ». Donc les 76 %, le κ et la stabilité de la diapositive 21 portent majoritairement sur
  une tâche que le banc n'exécute pas, et **la justesse sur la tâche réellement exécutée repose sur
  n = 6**. Ce découpage n'apparaissait nulle part dans le support. Réponse ajoutée en Q&A, placée
  avant celle du κ dont elle est la version plus tranchante : on ne déclare pas le n = 6, on conclut
  sur la **comparaison appariée** (même juge, mêmes 60 questions, même exécution), le témoin Lucene
  invariant et McNemar p = 0,0066. La note sort aussi, si on insiste, le `bruit_maitrise` **50 %**
  d'accord du fine-tuné — l'un des trois contrôles dont la conjonction fait le 48 % / 24 %. Ce que ça
  coûte : la valeur absolue des deux taux. Ce que ça ne coûte pas : leur écart. Hors écran, phase de
  coupe : 31,2 min inchangés. ⚠ Le renommage de la diapositive 24 **augmente** la probabilité de
  cette question au lieu de la réduire — c'est pourquoi elle est armée dans le même mouvement.

- **La diapositive 24 ne mesurait pas des réponses : la ligne portait un faux nom.**
  Elle affichait « Réponses justes 48 % / 24 % ». Ce chiffre est `passRate`, et `passRate` vaut PASS
  ⟺ les **trois** contrôles de contexte sont vrais — pertinent, suffisant, bruit maîtrisé
  (`RagContextJudge.java:93-95`, `RagQualityEvaluation.tauxPass:166`). Le banc ne génère aucune
  réponse : aucun appel de chat dans `RetrievalBenchmark.java`. Le seul chemin de génération qui
  existe, `RagService.askQuestion`, n'y est pas branché. Renommée **« Contexte exploitable »** à
  l'écran et à l'oral, avec la phrase « mon banc ne note pas des réponses : il note ce que chaque
  moteur rapporte ». Payée en coupant « les trente-six autres, les deux font pareil » — l'écran dit
  déjà que 24 questions départagent. 31,2 min inchangés. Les chiffres, eux, ne bougent pas : seul le
  nom était faux.

- **La diapositive 21 était coupée à la projection ; l'échafaudage ASCII est retiré.**
  Mesuré sur le rendu réel, pas sur le markdown : les 31 diapositives exportées en PNG, puis balayage
  des 12 dernières lignes de pixels de chacune. **Une seule touchait le bord bas**, la 21, avec 1819
  pixels de contenu dans la zone coupée — le schéma s'arrêtait en pleine ligne. Le bloc
  `CONFERENCE-V2.md:1153-1161` est supprimé, et **l'état 10 de `SCHEMA-ETATS.md` est fusionné dans
  l'état 11**, qui montre déjà le corpus en boîte à part et les deux cadrans. Conséquence sur le
  chemin critique : **dix dessins Excalidraw à faire deviennent neuf**. Re-mesure après coup : zéro
  diapositive sur 31 ne touche le bord. Le dépassement n'était pas un problème de contenu mais
  d'échafaudage — une image se dimensionne, pas du texte préformaté.

- **La « correction » du taux de contexte insuffisant était la régression, elle est annulée.**
  La diapositive 24 affichait 40 % / 66 % ; une correction écrite plus tôt le 2026-10-17 l'avait
  passée à 43 % / 67 % en recomptant sur `benchmarks/rag-quality-detail.jsonl` les **60** lignes,
  invalides comprises. Or le code exclut les invalides : `RagQualityEvaluation.ligneSynthese` divise
  par `valides`, pas par `js`. La source publiée, `benchmarks/rag-quality.jsonl` scénario
  `hybrid|hybrid` ligne `ALL`, donne `0,397` et `0,661` — soit **40 % / 66 %**, les valeurs
  d'origine, au même dénominateur (n = 58 et 59) que les 48 % / 24 % de la même ligne. La correction
  laissait donc deux dénominateurs sur une seule diapositive et contredisait les notes des
  diapositives 13 et 31, restées à 66 % contre 40 %. Elle se trompait aussi de sens : 40/66 fait
  26 points d'écart et 43/67 en fait 24 — elle **réduisait** l'écart au lieu de le flatter.
  **Leçon : recouper contre le fichier de synthèse publié avant de recalculer depuis le détail.**

- **Un item Lucene reste non réconcilié, et c'est écrit dans les notes.** En recomptant à la main sur
  le détail en excluant correctement les invalides, Neo4j tombe pile (39/59 = 0,661) mais Lucene
  donne 24/58 = 0,414 contre 23/58 = 0,397 au fichier de synthèse. Un item sur 58 : ne change ni le
  classement, ni « quatre fois sur dix ». **Ne pas afficher 41 % tant que l'item n'est pas trouvé.**

- **« Vingt-cinq points d'écart » dans le script est juste, et la note le protège désormais.**
  Sur les taux bruts 0,483 − 0,237 = 24,6 points ; le 24 vient des arrondis affichés. Vérifié avant
  d'éditer, donc rien touché.

- **La phrase éditoriale en attente est posée : le support dit maintenant à l'écran quel juge a
  tourné le banc.** La réserve de la diapositive 24 devient « Sur ce corpus, selon ma variante
  entraînée — 76 % de justesse, comme celle décrite », et le script l'énonce en trois phrases.
  Preuve directe et non plus déduite : les 120 lignes du scénario portent `judgeModel` =
  `…Qwen2.5-Coder-14B-Instruct-4bit+adapters/14b-judge-ckpt200`. Le piège κ est armé dans les notes :
  les deux variantes sont indiscernables **en justesse** (76 % contre 76 %), pas en alignement —
  κ 0,48 pour celle décrite diapositive 21, κ 0,44 pour celle qui a tourné le banc.
  Coût : +0,2 min (31,0 → 31,2).

- **Les trois items incorrigibles ont été lus, et l'étalon tient.** `JURY_RESULTAT.md` disait
  explicitement que distinguer « étiquette discutable » de « cas difficile » demandait de les lire,
  et que ça n'avait pas été fait. C'est fait. Dans les trois cas l'affirmation centrale de la copie
  est fausse et l'étalon la réfute par un contre-exemple vérifiable : `Arrays.asList` est une vue de
  taille fixe et non une liste immuable (`set` passe), `"2026-03-01"` est lu en UTC là où
  `"2026-03-01T00:00:00"` est lu en local (le correctif proposé **crée** le décalage), et le gel sous
  charge est un interblocage par ordre d'acquisition inversé et non de la contention.
  **Ce n'est donc pas un défaut de corpus.** La question « corpus ou modèle ? » est refermée : c'est
  le modèle.

- **Le motif commun est le résultat, et il n'a pas de test.** Dans les trois, l'erreur centrale est
  enrobée de développements annexes **exacts et bien écrits**. C'est le biais de verbosité dans sa
  forme adulte : la parade appariée de la diapositive 11 fait varier la **longueur** à défaut égal,
  pas la **densité de vrai autour du faux**. Elle ne peut pas couvrir ces trois-là, et les 46 % de
  faux PASS sur défauts bavards ne parlent pas d'eux. Piste outillable, **non mesurée** : un jeu
  apparié *erreur bien entourée* / *erreur nue*. n = 3, post hoc, fréquence inconnue.

- **Les diapositives 14 et 29 sont recalées — la dette est passée d'un plan à un résultat.** La 14
  ouvre une dette en une ligne (« mon juge est tout seul, j'y reviens à la fin ») que la 29
  remboursait par « un jury de familles disjointes ». Le jury ayant rendu 2/8, c'était faux à
  l'écran. **La 14 ne bouge pas d'un mot** — elle parle de famille, et la nouvelle conclusion aussi.
  La 29 dit désormais « je vous l'ai dit, alors je l'ai fait : 2 erreurs sur 8, et la même
  complaisance. Ce n'est pas la famille — c'est l'erreur bien entourée », et se ferme sur « pas un modèle de
  plus, un test de plus ».

- **L'objection « vos modèles sont trop petits » est armée hors écran**, avec cinq réponses dans
  l'ordre et la concession franche qui les rend crédibles. Le détail qui la désarme : le juge de
  l'autre famille était un **24B, plus gros que le 14B**, et il n'attrape que 2 sur 8 — « trop
  petit » n'explique pas ce résultat. Et la dernière ligne de la 29 pose la réponse **avant** la
  question.

- **Les trois items sont aussi matière parlée, à coût quasi nul.** Une phrase entre sur scène à la
  diapositive 22 (« une phrase fausse entourée de paragraphes justes — *Arrays.asList renvoie une
  liste immuable*, faux, et tout le reste est impeccable »), **payée** par la coupe du rappel
  redondant qui suivait : **+7 mots net**. Le reste vit dans les notes, y compris la formulation
  exacte à dire si quelqu'un reprend sur « vue de taille fixe » — à ne pas improviser devant 400
  personnes.

- **Minutage après les trois interventions du soir : 4339 mots = 31,0 min**, soit 11,0 min à couper.
  Détail du coût, mesuré et non estimé : option A resserrée sur la 21 **+20 mots**, phrase de la 22
  **+7**, réécriture de la 29 **+14** (écran +2, parlé +14). Aucune n'a été appliquée sans son
  chiffre.

- **`CONFERENCE-V2.html` est à jour** — rendu le 2026-10-17 à 16 h 57, **31 sections**, et le
  contenu neuf vérifié dans le rendu lui-même, pas seulement dans la source.

- **Le commit unique est fait** — `a376d69`, sur `talk/v1`, **non poussé**. (Le hash `f317add` noté plus tôt est l'objet d'AVANT l'amend : il existe encore mais n'est pas dans l'historique de la branche. Vérifié le 2026-10-17 par `git merge-base --is-ancestor`.) Il plie tout d'un coup :
  la quatrième ligne, les trois affirmations d'écran qu'elle a rendues fausses, la réponse hostile
  qui était fausse hors écran, la carte des dépendances, l'audit, le correctif du schéma, les deux
  pièges armés et le pré-enregistrement Mistral.

- **Le minutage était faux de 2 %, et c'est moi qui l'avais cassé en le remesurant.** Un recompte
  intermédiaire a donné **4453 mots** contre les 4207 publiés, et l'écart ne se raccordait pas à mon
  ajout d'environ 95 mots. Plutôt que de publier, j'ai cherché : mon compte prenait pour des mots les
  jetons de **ponctuation isolée** (« : », « ? » entourés d'espaces) et le terminateur `-->`, soit
  environ 5 mots par diapositive. La preuve qui tranche : la méthode corrigée, appliquée à la version
  commise, rend **4195 mots = 30,0 min**, donc les 30,1 min déjà publiés, et **seul le bloc 19-22
  bouge** dans le tableau par bloc — les sept autres sont inchangés au dixième près.
  **Chiffre juste : 30,7 min, 10,7 min à couper.** La diapositive 21 est désormais la plus chère du
  support, **2 min 20**, deux fois et demie la médiane qui est à 52 s.
  → Ce chiffre est celui sur lequel tu vas choisir les diapositives à retirer, d'où l'insistance.

- **Un piège de définition sur la colonne κ, trouvé parce que le contrôle a échoué.** En auditant les
  quatre chiffres de la quatrième ligne j'ai d'abord rendu **κ 0,53** pour la variante à conventions
  là où l'écran affiche **0,48**. Ce n'est pas l'écran qui a tort : la colonne du support est
  `kappa_mean`, la moyenne des trois passes, et j'avais calculé `kappa_majority`. Les deux clefs
  existent dans `metrics.json` et divergent de cinq centièmes sur le 14B (0,479 contre 0,529).
  Elles ne se séparent que lorsque le juge est **instable**, puisque le vote majoritaire lisse ce que
  la moyenne par passe subit. **Pour le 32B elles coïncident** (0,8011 et 0,8006) : le 0,80 affiché
  est donc juste dans les deux définitions — chance, pas méthode, et c'est écrit comme tel.
  → Consigné dans `demo/MINUTAGE-ET-AUDIT.md`. **Ne jamais comparer un κ du support à un κ recalculé
  sur le vote majoritaire** : cela fabrique un écart qui n'existe pas.

- **Un piège en moins, celui-là vérifié : l'ambiguïté du 76 % ne se reproduit pas sur la quatrième
  ligne.** Le dépôt publie une « Exactitude » qui est la moyenne des passes, l'écran montre le vote
  majoritaire — 73,3 % contre 76,0 % sur la variante à conventions, 71,3 % contre 76,0 % sur la
  fine-tunée. Pour le 32B les deux valent **90,0 %**. Cet écart **est** la valeur du vote par
  auto-cohérence, et il s'effondre quand le juge est déjà stable : il n'y a plus rien à départager.
  La question hostile « pourquoi deux exactitudes ? » ne porte donc que sur les trois premières lignes.

- **Balayage du plafond à l'écran : rien à corriger.** L'hypothèse de plafond étant morte, j'ai
  extrait la portion visible des 31 diapositives et cherché toute formulation de plafond. **Zéro
  occurrence à l'écran** ; les six occurrences du fichier sont toutes dans des notes, et toutes
  enregistrent l'abandon. L'inventaire des chiffres visibles est également ressorti, 15 valeurs
  distinctes, tous couverts par l'audit.

- **Une coupe gratuite de 30 à 42 s, trouvée en cartographiant les dépendances.** La dette ouverte
  diapositive 14 (« ne pas faire juger un modèle par sa propre famille, mon juge est tout seul,
  j'y reviens à la fin ») est réglée **deux fois** : diapositive 28 (70 mots, 30 s) et diapositive 29
  (98 mots, 42 s), avec la **même prémisse et le même 8/12**. Lequel garder est éditorial, donc à toi.
  Carte complète des renvois prononcés ajoutée à `demo/MINUTAGE-ET-AUDIT.md` — elle dit aussi ce
  qu'on ne peut **pas** couper : la chaîne cumulative des 9 marqueurs de schéma (9→10→11→12→13→16→17→20→21),
  et les deux ancrages de la 16 (diapos 7 et 15).
  Contrôle : le découpage retrouve les 31 `<section>` du HTML **et** place les 9 marqueurs exactement
  là où `SCHEMA-ETATS.md` les avait recalés hier — la même conclusion par un autre chemin.
- **Vérifié, et le pré-enregistrement n'est pas amendé.** La duplication ci-dessus posait la question :
  un résultat Mistral ≤ 3/8 oblige-t-il à changer la **28** autant que la **29** ? Non. La 28 ne
  promet aucun jury, elle ne constate que « rejouer le même modèle ne fait varier que
  l'échantillonnage » — qu'une autre famille échoue aussi ne la contredit pas. `PREENREGISTREMENT_JURY.md`
  a donc raison de ne viser que la 29.
- **Un écrasement silencieux désamorcé avant qu'il se produise.** Chaque banc réécrit
  `results/metrics.json` avec sa seule variante, et `results/` n'est pas versionné : à la fin du
  banc 32B, les trois variantes du rapport publié auraient disparu. Trouvé en lisant ce que
  `benchmark_judges.py` sérialise (ligne 914, `serializable` ne contient que les variantes
  sélectionnées) plutôt qu'en supposant une fusion. Sauvegardé, puis prouvé réparable gratuitement.
- **Les deux images du support sont prêtes à être écrasées, sans autre travail.** Vérifié : les
  gabarits `img/ollamassist-marketplace.png` et `img/qr-feedback.png` sont **déjà aux dimensions
  exactes** que les notes demandent (768 × 638 et 620 × 620, soit le double de l'affichage). Écraser
  les deux fichiers au même nom et relancer le rendu suffit — **aucune modification du markdown, ni
  du HTML**. Ce sont les deux seules images référencées par le support.
  ⚠️ `img/judge_dredd_casque.jpeg` n'est référencé **nulle part** : reste d'une diapositive coupée,
  ou image jamais branchée. À trancher par toi, le fichier n'est pas supprimé.

- **Le support est minuté : 30,1 min pour une cible de 20.** Script parlé seul, 4207 mots à
  140 mots/min ; contrôle de lecture, le découpage retrouve les 31 `<section>` du HTML. Nouveau
  document `demo/MINUTAGE-ET-AUDIT.md` : prix de chaque diapositive, et des blocs.
  **Le fait qui change la stratégie de coupe : le support est plat.** La plus longue diapositive fait
  1 min 47, la médiane à peine moins d'une minute. Rogner les huit plus longues de 30 % ne rendrait
  que ~2 min sur 10. **Les 10 minutes sont dans le NOMBRE de diapositives, pas dans du gras** — il
  faut en retirer une dizaine. Retirer 10 diapos de méthode (moyenne 0,93 min) amène à 20,7 min.
  Et la mesure **confirme la ligne éditoriale par le chiffre** : méthode (6-18, 13 diapos) =
  **12,1 min = 40 %** du temps, preuves (23-26, 4 diapos) = **4,5 min = 15 %**. Le choix des
  diapositives reste éditorial et n'a pas été fait.
- **Les renvois du schéma étaient périmés, et ça aurait coûté 2-3 h de dessin.** `SCHEMA-ETATS.md`
  faisait pointer les états **3 à 10 une diapositive trop loin**, et les états 1 et 2 ont fusionné en
  **un seul marqueur** (diapo 9) depuis la suppression de « quand évaluer ? » le 2026-10-14. Recalé
  par le CONTENU des marqueurs, pas par leur numéro. Contrôle : 9 marqueurs `[AJOUT AU SCHÉMA]`
  (diapos 9, 10, 11, 12, 13, 16, 17, 20, 21) + l'état 11 en récapitulatif = **les dix états à
  dessiner**, ce qui recoupe le chemin critique. Deux avertissements ajoutés en en-tête, dont :
  **ne pas recopier « κ 0,880 » tel quel** dans les états 10 et 11 — c'est le κ rétrogradé.
- **Septième chiffre faux retiré de l'écran — diapositive 24.** La ligne « contexte jugé
  insuffisant » affichait **40 % / 66 %**. Recalculé depuis `benchmarks/rag-quality-detail.jsonl`
  (scénario `hybrid|hybrid`, contrôle `contexte_suffisant` à faux) : **lucene 26/60 = 43,3 %**,
  **neo4j 40/60 = 66,7 %**. Affiché désormais **43 % / 67 %**. Le 40 % était faux de 3 points et
  **dans le sens qui flatte la conclusion** : 26 points d'écart au lieu de 24. Vérifié qu'aucun autre
  contrôle ne produit 40 % (`contexte_pertinent` 38,3/45,0 · `bruit_maitrise` 26,7/26,7), donc ce
  n'était pas une autre mesure mal étiquetée.
- **Le reste de l'audit passe, au chiffre près**, parseur du harnais importé pour la justesse :
  diapos 11 (46 %), 12 (12/60), 13 (27/23 → 17/10/21, 76 %), 18 (47/50 · 17 incises · 30/30),
  21 (κ et stabilités), 24 (48,3 / 23,7 · 24 départagent 19–5), 25 (22,0 % · Lucene inchangé),
  26 (8–0 · 5/7 · 6/9, totaux retombent sur 24 et 19).
- **L'audit des chiffres affichés est maintenant complet.** Les diapositives que la passe d'hier
  n'avait pas couvertes sont vérifiées : **14, 19 et 20 ne portent aucun chiffre à l'écran** (la 20
  n'affiche que le schéma ASCII) ; la **23** (« 60 questions, les mêmes pour les deux stratégies »)
  retombe sur les 240 lignes de `rag-quality-detail.jsonl` = 60 × 2 stratégies × 2 scénarios ; la
  **27** tient sur ses deux chiffres — « 150 réponses » = 50 items × 3 passes, et la « dégradation de
  76 % » est le **miroir exact** du +76,0 points que `report.md` publie pour `nu → conventions`
  (IC95 [+64, +88], McNemar p = 0,0000) : l'adaptateur ignoré faisait servir la variante fine-tunée
  **sans ses conventions**, donc à 0 %. Formulation d'origine retrouvée dans `CONFERENCE-2026.md`
  ligne 1197 — « le fine-tuning dégrade la justesse de 76 % » — ce qui confirme la lecture.
  Restent hors de portée : les citations externes des diapositives 2 à 5, qui ne sont pas dans le dépôt.
- **La diapositive 22 passe au chiffre près**, et elle n'était pas dans la passe d'hier : 50 copies,
  38 stables / 12 instables, « 12 relectures au lieu de 50 » = 76 % du travail écarté, « 4 de ses 12
  erreurs » et les 8 manquées — tout recoupe `TRIAGE_POSTHOC.md`. Le 8/12 répété diapos 28 et 29
  est juste lui aussi.
  **Un piège trouvé au passage, armé hors écran** : la 21 affiche 76 % de justesse (= **38** copies
  justes) et la 22 affiche **38** stables. Deux 38 sans rapport — les 38 stables contiennent
  **8 copies fausses**. Note de mise en garde ajoutée aux notes de la 22, avec la phrase de réponse
  si quelqu'un fait le rapprochement.
- **Deux ambiguïtés armées hors écran.** (a) Le **76 %** est le *vote majoritaire* ; `report.md`
  publie aussi « Exactitude **73 %** », la moyenne des trois passes (70, 76, 74). Les deux sont
  justes, ce sont deux estimateurs — réponse courte notée en diapositive 13. (b) Le **12/60** de la
  diapositive 12 **sous-estime** le biais : les 12 bascules surviennent parmi les **39** questions à
  contenu identique, soit 31 % et non 20 %. La formulation affichée est donc conservatrice.
  **Témoin trouvé au passage, et il est net** : rejoué *avec* la graine, le même bras Lucene donne
  **0 bascule sur 60** et 60/60 hintCoverage identiques entre les deux scénarios.

- **La diapositive 21 devient le tableau des variantes** (`REX_TRAME.md:257`, 450 générations). Les
  trois lignes κ / stabilité / hintCoverage sont remplacées par `invite nue` · `+ 4 conventions` ·
  `+ entraînement` × justesse / accord / stabilité / schéma. Motif : **un chiffre faible seul est une
  note, le même entouré de ses voisins de même nature est une information.** Le 0,44 n'est plus un
  bulletin, c'est la cellule qui prouve que l'entraînement n'a pas acheté le jugement. hintCoverage
  sort — il est déjà sur « Le résultat », à sa place.
- **Fusion 20+21 écartée.** La 20 pose la question, la 21 répond : les notes de la 20 l'exigent
  (« ne pas annoncer la réponse ici »), et c'est aussi ce que fait le support de Villaren. Le support
  reste donc à **31 diapositives** — la coupe des 12 minutes devra venir d'ailleurs.
- **Sixième fausse affirmation retirée de l'écran.** La diapositive 29 disait « Pas un plus gros
  modèle — mesuré, **76,0 % contre 76,0 %** ». Faux : le 32B n'a jamais été entraîné
  (`REX_TRAME.md:431`) et ce chiffre est `14B-baseline-conventions` contre `14B-finetuned`, deux
  variantes de **même taille**. La feuille de route ne cite plus de chiffre et renvoie au tableau.

- **Famille disjointe déclarée** — `Mistral-24B-baseline-conventions` dans `configs/variants.json`
  (port 8085, aucun adaptateur, **le même** `configs/conventions.md`), avec sa paire de comparaison.
  Mistral Small 3.2 plutôt que Gemma 3 : Gemma traite le rôle `system` autrement, et un suffixe non
  appliqué en silence rendrait une ligne d'apparence normale sur un juge sans conventions — le mode
  de défaillance dont l'exposé fait sa conclusion. Lecture fixée avant mesure dans
  `PREENREGISTREMENT_JURY.md`, avec son **seuil de coût** (au-delà de 25 relectures sur 50, levier
  trop cher quelle que soit sa couverture). **Non lancé** : le 32B occupe la machine.
- **Mesuré au passage, et nulle part ailleurs dans le dépôt : « systématique » n'est pas une
  propriété de l'item.** Des 8 erreurs systématiques du juge à conventions, l'entraînement en
  **corrige 3**, en rend **4 instables** — donc rattrapables par le triage — et n'en laisse **qu'une**
  systématique (`b03-014`, le seul item que les deux juges ratent trois fois sur trois). Un simple
  changement d'entraînement déplace donc **7 des 8** angles morts. Ce 3/8 corrigé devient le plancher
  que le jury doit battre pour valoir mieux qu'un entraînement de plus. Obtenu en réutilisant
  `extract_judgment` du harnais, et **recoupé** contre les effectifs publiés de `TRIAGE_POSTHOC.md`
  (38/30/8/12/8/4 et 29/24/5/21/14/7 reproduits à l'identique) avant d'émettre la moindre cible.
- **Contradiction 22/29 relevée**, versée à l'arbitrage ouvert ci-dessus. Rien n'a été corrigé à
  l'écran : les deux branches ont un coût, c'est une décision éditoriale.
- **Veille système** — la machine était réglée sur `sleep 1` min, retenue seulement par l'assertion
  « display is on » de `powerd` et `displaysleep 180`. Le banc 32B demande ~3 h 08 : l'écran se serait
  éteint **avant la fin**, et la machine aurait dormi une minute après. `caffeinate -i -w <pid>` posé,
  il s'arrête avec le banc. À refaire avant tout banc long. Le capot rabattu endort malgré tout.

- **Arbitrage tranché : tout le support en « à conventions ».** Diapositive **22** alignée sur les
  quatre preuves — 38/12 au lieu de 29/21, **12 relectures au lieu de 50**, et **4 désaccords sur 12**
  rattrapés au lieu de 7, les **8 autres** systématiques. Ses notes étaient *déjà* écrites pour ce
  juge (« relire 16 au lieu de 12 et rattraper les mêmes 4 », « pourquoi les 8 échappent ») : c'était
  une restauration, comme la 21. Diapositive **14** suivie : matrice **17/10/21**, « près de
  4 défauts sur 10 », verbosité 46 %/40 %, PASS 65 %. La 29 (« 8 erreurs sur 12 ») devient juste
  sans y toucher. Script parlé réécrit aux deux endroits, notes d'arbitrage datées à la place des
  anciennes. 31 sections rendues.
- **Ce que l'arbitrage coûte, mesuré et non supposé** : la 22 perd de la couverture (4/12 au lieu de
  7/12) mais gagne en économie (12 relectures au lieu de 21), et elle **installe mieux la 29** — 8
  erreurs systématiques à attaquer au lieu de 5. Sur la 14, aucun chiffre ne bouge de plus de
  4 points. La matrice publiée (16/11/22) a été reproduite à l'identique comme contrôle avant
  d'émettre le moindre nouveau chiffre.
- **Mesures gratuites relevées, aucune machine consommée** — à garder **hors écran** pour les
  questions, phase de coupe oblige :
  - **noyau d'erreurs commun** : les deux juges ont **12** désaccords chacun, **6 communs** seulement,
    union **18 sur 50**. La moitié des erreurs n'est donc pas partagée entre deux juges de la même
    famille qui ne diffèrent que par l'entraînement — ça rend le pari « familles disjointes »
    crédible, et ça donne une référence au banc Mistral.
  - **coût réel** : **0,30 à 0,38 $ pour mille jugements** (`metrics.json`,
    `cost_per_1k_judgments_usd`, déjà calculé et jamais utilisé). Seul candidat à l'écran, et
    seulement en remplacement d'une ligne de méthode.
  - **les 450 générations ont coûté 3,15 h et 441 721 jetons** (314 220 entrée / 127 501 sortie).

## Backlog technique, après l'exposé

- **Construction du graphe via bytecode** (ASM/ByteBuddy au lieu de JavaParser) — *priorité haute*.
  JavaParser rate lambdas, références de méthode et classes anonymes, donc les relations CALLS/EXTENDS
  sont incomplètes et l'expansion K-hop travaille sur un graphe troué. C'est la piste la plus crédible
  pour que Neo4j rattrape Lucene sur CROSS_MODULE — le seul niveau où l'écart conclut aujourd'hui.
- **Cross-encoder reranker** local (BGE) à la place de `LLMReranker` : 10 à 50× plus rapide.
- **Multi-query retrieval** : N variantes de la question, fusion RRF.
- **Comparaison de modèles d'embedding** : voyage-code-3, jina-embeddings-v3.

## 2026-10-19 — bancs notation, échelle, et le plafond de 6000 caractères

- **Campagne RAG close à deux juges.** gemma-4-26b-a4b déclaré inutilisable une seconde fois
  (38 INVALID sur 238 à 4096 jetons, seuil 18/360) ; run écarté de `benchmarks/`. Conséquence à
  assumer : les deux juges restants sont **le même modèle**, le contrôle de parenté de famille
  n'existe plus. La phrase que `rapport_campagne.py` génère à ce sujet ne doit pas aller à l'écran.
- **Diagnostic de budget** (`PREENREGISTREMENT_SCHEMA.md`, relance 1) : **35/37** items redevenus
  analysables à 2048 jetons. Seuil ≥ 28 ⇒ effet de budget, pas de format.
- **Banc permutation** (`PREENREGISTREMENT_NOTATION.md`) : 120 jugements, témoin propre,
  **0 retournement** des deux côtés, amplitude de note nulle sur 12 items. Lecture déclarée :
  rien ne va à l'écran. L'instabilité de la notation n'est pas reproduite à température 0.
- **Banc échelle** (`PREENREGISTREMENT_ECHELLE.md`) : 180 notes, 0 échec. **4 valeurs vivantes
  sur 11** (1 ×70, 10 ×67, 6 ×28, 0 ×13) ⇒ va à l'écran. κ note/verdict = **0,918**. Même ordre
  des bras par la note et par le verdict ⇒ concordance à l'écran.
- **Plafond de 6000 caractères — à traiter le 2026-10-20.** Mesuré : vector-bm25 coupé **46/60**
  (médiane 4 179 car. perdus), vector 10/60, graphrag 1/60. Couverture sans LLM, vue contre réelle :
  vector-bm25 **68,6 → 87,4 %**, vector 75,0 → 76,7 %, graphrag 59,6 → 59,6 %. Donc le « non
  concluant » de la paire principale est un aveuglement de l'appareil, et le classement
  `vector > vector-bm25` corroboré sans LLM **s'inverse** sans le plafond. Les conclusions contre
  graphrag, elles, sont renforcées. À faire : pré-enregistrer plafond/paire/lecture, **fixer
  `num_ctx` explicitement** (son défaut tronque l'invite en silence), puis rejuger les 180.
- Outils ajoutés : `scripts/banc_notation.py`, `scripts/banc_echelle.py`, `scripts/java_ordre.py`
  (réplique vérifiée de l'ordre et de la troncature Java), `scripts/rapport_notation.py`,
  `scripts/rapport_echelle.py`.

### File du 2026-10-20 — **faite**, voir la section suivante

---

## 2026-10-20 — le plafond tombe, et l'échelle se réduit à trois crans

Deux bancs pré-enregistrés avant le premier jugement, lancés en chaîne, **0 échec sur 540
jugements**. `benchmarks/PREENREGISTREMENT_PLAFOND.md` et
`benchmarks/PREENREGISTREMENT_NOTE_BC.md` portent le dispositif, la lecture et le résultat.

### Banc plafond — la paire principale n'était pas à égalité, elle était mal mesurée

`RagContextJudge` coupait le contexte à 6000 caractères **après** le mélange, ce qui touchait
57/180 contextes et **46/60 du seul bras `vector-bm25`**. Rejugés sans plafond :

| bras | avec plafond | sans plafond | écart |
|---|---|---|---|
| `vector` | 55,0 % | 60,0 % | +5,0 |
| `vector-bm25` | 48,3 % | **78,3 %** | **+30,0** |
| `graphrag` | 16,7 % | 16,7 % | 0,0 |

- **Q1, principale** — `vector` ↔ `vector-bm25` sans plafond : **+18,3 pts en faveur de
  `vector-bm25`**, discordantes **11 contre 0**, **p = 0,0010**. La lecture déclarée dit : le
  chiffre va à l'écran. **Le « non concluant » était une cécité de l'appareil.**
- **Q2** — sur les 57 contextes tronqués, 49,1 % → 86,0 % de PASS, **21 FAIL→PASS et 0
  PASS→FAIL**. La bascule est unilatérale : couper n'a jamais aidé un contexte.
- **Q3, secondaire** — `graphrag` passe de −31,7 pts à **−61,7 pts** (p < 0,0001). La
  conclusion sur `graphrag` est **renforcée**, le biais jouait contre elle.
- **Contrôles** : 0 échec ; **0 verdict changé** sur les 123 contextes intacts ; contrôle de
  reproduction **12/12** → `num_ctx` (4096 par défaut → 20480) ne change aucun verdict, et le
  bras A en banque reste valide. L'invite la plus longue sous plafond pesait 8020 caractères :
  **le piège `num_ctx` ne nous avait pas touchés.**
- **Le signal non-LLM concorde enfin** : couverture réelle 87,4 % (`vector-bm25`) contre
  76,7 % (`vector`). Avec plafond, banc et signal se contredisaient.

### Bras B et C — l'échelle de 0 à 10 est un interrupteur déguisé

| bras | distribution | valeurs vivantes (≥5/180) | κ contre le verdict de A | note moyenne |
|---|---|---|---|---|
| **B** — note seule, sans critères | `0×128 2×21 5×2 6×1 8×25 10×3` | **3** (0, 2, 8) | 0,381 | 1,60 |
| **C** — note seule, critères énoncés | `0×44 1×2 2×42 3×2 5×1 6×9 7×12 8×68` | **5** (0, 2, 6, 7, 8) | 0,841 | 4,33 |

- **Va à l'écran** (Q1, seuil déclaré ≤ 4) : **B utilise 3 valeurs sur 11, et rend zéro dans
  71 % des cas.** C'est la pratique courante — « note ce contexte de 0 à 10 » — et elle ne
  produit pas une échelle.
- **Brut, pas écran** : C reste à 5 valeurs vivantes, au-dessus du seuil.
- **Q3 — la phrase « la note décide pareil » est INTERDITE** : B classe
  `vector-bm25 > vector`, A et C l'inverse. Lecture déclarée appliquée.
- **Q4** — énoncer les critères sans les faire sortir déplace la note moyenne de **+2,73
  points sur 10** et fait passer κ de 0,381 à 0,841. κ(B, C) = 0,278, notes identiques 46,1 %.
  **Ce n'est pas l'échelle qui porte l'information, c'est le cadrage.**
- **Post hoc, noté, non présentable** : l'ordre rendu par B est celui que le banc plafond
  établit comme correct — mais A et C ont tourné **sous le plafond**. Les rapprocher demande
  de rejouer B et C sans plafond, et un nouveau pré-enregistrement.

### Ce que ça change dans la présentation

1. La conclusion 4 change de chiffre **et de sens sur la paire principale** :
   `vector-bm25` bat `vector` de 18,3 pts (p = 0,0010), et `graphrag` tombe à −61,7 pts.
   La phrase « indiscernables » doit **sortir**.
2. Une leçon neuve et chiffrée sur le plafond lui-même : **un détail d'implémentation du
   harnais — couper le contexte à 6000 caractères — inversait le classement.** 21 verdicts
   basculent, tous dans le même sens.
3. La leçon sur la notation existe enfin sans confusion : **3 valeurs sur 11**.

### Outils ajoutés

`scripts/banc_jour2.py` (quatre dispositifs, une seule invite partagée),
`scripts/banc_jour2.sh` (enchaînement + `caffeinate`), `scripts/controle_repro.py`,
`scripts/rapport_plafond.py`, `scripts/rapport_note_bc.py`. `scripts/java_ordre.py` accepte
désormais `plafond=None`, le défaut 6000 restant vérifié identique sur les 180 contextes.

### File, dans cet ordre

1. **Corriger le plafond dans le code**, pas seulement dans le banc : `RagContextJudge`
   tronque toujours à 6000 caractères, et `num_ctx` n'est fixé nulle part dans le dépôt.
2. **Museler ou qualifier** la phrase auto-générée « la parenté de famille générateur/juge
   n'a pas porté le résultat » dans `scripts/rapport_campagne.py` : le contrôle est **vide**,
   les deux juges restants sont le même modèle.
3. Reporter les nouveaux chiffres dans les supports (`demo/llm-as-a-judge/`, `REX_TRAME.md`).

### Soir — JURY2, et le plafond de sortie qui recommence

`judge-finetune/PREENREGISTREMENT_JURY2.md`, écrit **avant la première génération** Gemma.
Deuxième tentative de jury après le 2/8 du 2026-10-17, mais la question a changé : population
8 items → **50**, métrique « corrections » → **justesse du vote**, comparateur 3/8 → **45/50**
(le 32B seul). Trois familles, un vote chacun : Qwen2.5-Coder-32B et Mistral-24B **déjà en
banque**, seul Gemma-4-31B reste à jouer — le banc coûte **un run, pas trois**.

Ce qui a motivé la relance, mesuré sans dépenser un jeton, en rejouant les runs en banque :

| variante | justes | indulgent | sévère | p binomial |
|---|---|---|---|---|
| few-shot | 34 | 15 | 1 | 0,0005 |
| conventions | 38 | 10 | 2 | 0,0386 |
| fine-tunée | 38 | 11 | 1 | 0,0063 |
| 32B | 45 | 4 | 1 | 0,3750 |
| Mistral-24B | 35 | 15 | 0 | 0,0001 |
| **total** | | **55** | **5** | **≈ 10⁻¹²** |

Et le **jury simulé** sur ces 5 configurations : **38/50 = 76 %**, 12 erreurs **toutes
indulgentes**, contre **45/50 = 90 %** pour le 32B seul. Les deux chiffres sont **post hoc**,
et le vote est pondéré 4 Qwen pour 1 Mistral : ils motivent le banc, ils ne le remplacent pas.
L'étalon est quasi équilibré (27 FAIL / 23 PASS) : la direction n'est pas un artefact.

- **Dépouillement écrit avant le chiffre** : `judge-finetune/scripts/rapport_jury2.py`,
  réutilisant `extract_judgment` du harnais pour qu'aucune seconde logique de lecture ne
  diverge. **Témoin** : il reproduit les 10/150 non extractibles de Mistral (6,7 % publiés).
- Variante ajoutée à `configs/variants.json` par **insertion ciblée**, jamais par recréation,
  avec sa paire de comparaison déclarée. Sauvegarde avant modification.
- **Sonde déclarée** : 3 items, **3/3 extractibles ⇒ lancement**, ≤ 2/3 ⇒ JURY2 meurt et
  aucune quatrième famille n'est essayée. Passée 3/3.

#### L'incident : le plafond de sortie a mordu une famille sur trois

À 37 générations sur 150, inspection du run en cours : **9 sorties sur 36 exactement à 1024
jetons**, et les **8 verdicts non extractibles étaient exactement les 9 tronquées**.
Projection 33/150, contre un garde-fou déclaré à 15.

| variante | max jetons de sortie | médiane | au plafond 1024 |
|---|---|---|---|
| Qwen-32B | 818 | 415 | 0 / 150 |
| Mistral-24B | 429 | 238 | 0 / 150 |
| few-shot | 960 | — | 0 / 150 |
| fine-tunée | 813 | — | 0 / 150 |
| **Gemma-4-31B** | **1024** | **857** | **9 / 36** |

Le plafond **n'a jamais contraint deux familles sur trois et annulait la troisième** : un
réglage identique pour tous n'est pas un réglage neutre. C'est la **même forme** que le
plafond de 6000 caractères du matin, qui coupait 46/60 du seul bras `vector-bm25`, et la
**troisième occurrence** du piège dans le projet après les 37 INVALID du défaut MLX à 512.

Décision, et son prix : run **arrêté**, 37 générations **archivées** dans
`results/invalide-20261020-gemma-plafond-1024/` pour que les chiffres ci-dessus restent
auditables, **amendement daté** (20 h 48) ajouté au pré-enregistrement avec les deux tables
de jetons, et **nouveau contrôle** inscrit dans `rapport_jury2.py` :

```python
PLAFOND_SORTIE = 2048   # >0 sortie au plafond ⇒ variante ANNULÉE
```

Ce contrôle interdit une **seconde** remontée : si 2048 mord encore, la variante tombe, on ne
renégocie pas une troisième fois. Relancé à 2048 (`nohup caffeinate -i ./scripts/bench_variant.sh
Gemma-4-31B-baseline-conventions --max-tokens 2048`), ~143 s par génération, **fin attendue
vers 03 h 00**. Dépouillement : `cd judge-finetune && .venv/bin/python -I scripts/rapport_jury2.py`.

> Un run mono-variante écrase `metrics.json` : prévoir une reconstruction `--report-only`
> après coup, comme le 2026-10-17.

## 2026-10-21 — JURY2 : deuxième non concluant, et le juré qu'on a failli disqualifier

Run Gemma terminé (150/150). Dépouillement par `scripts/rapport_jury2.py`, écrit avant le
premier verdict. Résultat complet dans `judge-finetune/PREENREGISTREMENT_JURY2.md`.

**Garde-fous passés** : Gemma **0 non extractible sur 150**, **0 sortie au plafond de 2048**.
Les 8 verdicts perdus la veille venaient du plafond de 1024, pas du modèle.

- **Q1, principale** — jury des 3 familles **47/50 = 94 %** contre **45/50 = 90 %** pour le
  32B seul. Discordantes **2 contre 0**, McNemar exact **p = 0,5000**. **NON CONCLUANT**, et
  c'est le mot qui va à l'écran. La diapositive 29 ne gagne pas son chiffre : deuxième
  tentative de jury, deuxième non concluant — mais cette fois sur la bonne population et la
  bonne métrique, ce qui est en soi un résultat propre.
- **Q2** — Gemma : **1 indulgent, 0 sévère**, p = 1,0000. Sens rapporté brut, **sans la
  phrase**. L'indulgence ne gagne **pas** de confirmation par une troisième famille : avec une
  seule erreur, il n'y a rien à conclure sur sa direction. Le 55 contre 5 reste porté par les
  configurations en banque, et reste post hoc.
- **Q3** — les 3 erreurs du jury sont **toutes indulgentes**.

**Brut, noté, non présentable** : **Gemma seul rend 49/50**, contre 45/50 (Qwen) et 35/50
(Mistral). Discordantes Gemma/Qwen **4–0**, p = 0,1250, accord 46/50, et l'unique erreur de
Gemma est aussi une erreur de Qwen. Ce n'est pas une question déclarée de ce banc, et 8 points
à n = 50 tombent dans la zone que le dispositif ne tranche pas (seuil ~15 points,
`PREENREGISTREMENT.md` § 5). Consigné, pas exploité : l'exploiter demande un nouveau
pré-enregistrement.

Deux observations post hoc à ne pas mettre à l'écran en l'état, mais qui orientent la suite :
le vote majoritaire **tire le jury sous son meilleur juré** (47 contre 49) parce qu'un juré à
35/50 pèse autant que les autres ; et la famille qu'on a failli annuler pour un défaut de
harnais est la plus juste des trois.

### File, mise à jour

0. Reconstruire `metrics.json` (`--report-only`) : le run mono-variante l'a écrasé.
1. **Corriger le plafond de 6000 dans `RagContextJudge`** et fixer `num_ctx` dans le dépôt.
2. **Museler** la phrase auto-générée sur la parenté de famille dans `rapport_campagne.py`.
3. Reporter les chiffres dans `demo/llm-as-a-judge/` et `REX_TRAME.md`, **diapositive 29
   comprise** : le jury y reste une piste, désormais avec deux mesures non concluantes.
