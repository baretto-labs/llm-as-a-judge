# Audit du corpus — 2026-09-15

Audit conduit par un agent au contexte vierge, à qui aucune conclusion n'avait été transmise. Chaque
constat ci-dessous a été **re-mesuré indépendamment** avant d'être retenu ; les chiffres sont ceux de la
contre-mesure, pas ceux du rapport d'origine.

Le corpus était clos à 200 exemples, 0 erreur de validation, toutes les cibles déclarées atteintes. L'audit
montre que ces cibles portaient sur la composition, jamais sur ce que le corpus **enseigne**.

## 1. Le corpus enseigne le biais de verbosité, en sens inverse de son intention

La longueur du contenu évalué prédit le verdict, dans le sens « long ⇒ PASS ».

| Tâche | méd. PASS | méd. FAIL | meilleur seuil | exactitude | base |
|---|---|---|---|---|---|
| `CODE_ANALYSIS` | 1121 | 611 | 670 car. | **75,3 %** | 53,3 % |
| `RAG_FAITHFULNESS` | 734 | 342 | 666 car. | **84,0 %** | 56,0 % |
| `RAG_CONTEXT_RELEVANCE` | 1214 | 1206 | 1533 car. | 60,0 % | 56,0 % |

Une règle à seuil unique, qui ne lit **jamais** le code, atteint 75 % sur le code et 84 % sur la fidélité.
Une régression logistique en validation croisée groupée par `famille`, features toutes dérivables du prompt,
confirme : 73,8 % sur `CODE_ANALYSIS`.

Mesure importante : le contenu réellement évalué n'est pas le même selon la tâche. Pour
`RAG_CONTEXT_RELEVANCE`, la « sortie » est un placeholder constant de 126 caractères et le contenu à juger
est le **contexte**. Calculée sur le bon champ, la pertinence RAG est **saine** (1214 contre 1206, écart
nul) — une première statistique globale la comptait à tort comme fautive.

Cause : réflexe d'auteur. Les bonnes réponses ont été écrites longues et argumentées, les mauvaises courtes
et bâclées. L'écart est localisé — `generation` +714 car., `refactoring` +518, `question_reponse` +452,
contre `debogage` +166 et `explication` +95.

## 2. Le test de résistance au biais de verbosité ne mesure pas ce qu'il annonce

Sur le golden set, les deux groupes de la métrique n°3 (`PROTOCOLE.md`) :

- verbeux + FAIL (7 items) : 735, 918, 925, 1082, 1169, 1203, **1363** car.
- verbeux + PASS (3 items) : **1588**, 1699, 1846 car.

**Aucun chevauchement.** Un juge appliquant « ≥ 1500 caractères ⇒ PASS » — donc maximalement biaisé par la
verbosité — obtient 0 % de faux PASS sur les défauts verbeux, 100 % sur le contrôle inverse, et franchit le
critère de qualification « faux PASS ≤ 20 % ». Le test récompense le biais qu'il prétend détecter.

## 3. `RAG_FAITHFULNESS` est dégénéré

`citations_exactes` vaut `true` **25 fois sur 25** : polarité unique, ce que `PLAN_CORPUS.md` interdit
explicitement (« un contrôle à polarité unique enseigne un raccourci par nom »). L'équilibrage de polarité
avait été vérifié sur les 9 contrôles **supplémentaires**, jamais sur les contrôles de socle.

La famille « citation déformée d'un extrait », prévue au plan de la passe B, n'a jamais été produite :
c'était la seule qui aurait mis ce contrôle à `false`.

Conséquence : le triplet de socle n'a que **2 états** sur 25 exemples — `[V,V,V]` pour les 14 PASS,
`[F,F,V]` pour les 11 FAIL —, `absence_invention` est parfaitement colinéaire à `affirmations_etayees`, et
la métrique n°2 du benchmark (« accord par contrôle atomique : c'est lui qui dit *quel* critère le juge
rate ») n'a presque pas de matière. À titre de comparaison : `CODE_ANALYSIS` présente 6 états distincts,
`RAG_CONTEXT_RELEVANCE` 5.

## 4. Fuites d'annotation dans la cible

Le message assistant est ce que le modèle apprend à produire. Deux éléments n'y avaient rien à faire :

- **`meta.cas` recopié** : `Synthèse : cas limite.` ouvrait l'étape 3 de **40 cibles sur 40** juste avant le
  verdict. On apprenait au juge à annoncer une catégorie d'annotation qui n'existe pas à l'inférence.
- **Revendications d'exécution** : 104 occurrences en 61 tournures (« Vérifié par exécution », « mesuré
  par exécution »…). Excellente pratique de **production** du corpus, recopiée à tort dans la cible : on
  enseigne au juge à affirmer une preuve empirique qu'il ne peut pas produire au moment où il juge. C'est un
  vecteur d'hallucination, sur un modèle dont la rigueur est la seule raison d'être.

## 5. Fuite train/test propre au RAG

Les 50 exemples RAG ne reposent que sur **20 contextes distincts**, déclinés sous des familles différentes
— donc séparables par le split, que le groupement par `famille` n'empêche pas.

- contexte déjà vu en train/valid : **9 / 11** items RAG du golden set
- contexte **et** requête déjà vus : **8 / 11**

Or ces 11 items sont, depuis l'amendement du protocole, le seul instrument de surveillance de la posture
monde fermé. L'instrument censé valider l'objectif central est le plus contaminé du dispositif.

Conséquence directe d'un choix assumé dans `PLAN_CORPUS.md` (« un même symbole extrait par les deux moteurs
compte pour deux contextes distincts ») : le choix reste défendable pour l'entraînement, il ne l'est pas
pour le golden set.

## 6. Défauts mineurs

- `b13-007` et `b14-008` portent `verbeux=True` alors que leur sortie est le placeholder constant de 126
  caractères : la verbosité est dans le contexte, pas dans la sortie évaluée.
- **192 familles pour 200 exemples, dont 184 de taille 1.** Le mécanisme anti-fuite par `famille` est donc
  quasi vacant : le split est en pratique un tirage par exemple, et les paires contrastives se réduisent à 8.
- 12 des 18 noms de contrôle ont une description unique et fixe : la correspondance nom → description est
  apprenable par cœur, ce qui affaiblit l'argument « le juge doit lire la rubrique ».
- Repli `MAXLEN=1024` du 32B : p50 = 940, p90 = 1116 — une fraction serait tronquée. Compte exact non calculé.

## Ce qui est solide, et démontré

- **Longueur en tokens : aucun problème.** Vrai tokenizer Qwen 14B : maximum **1380**, p95 = 1164,
  **0/200 dépassent 2048**. Aucune complétion tronquée, aucun JSON de verdict coupé.
- **Aucun templating du raisonnement.** 99,2 % des 8-grammes des `<thinking>` et 100 % de ceux des `reason`
  sont des hapax ; similarité inter-exemples (jaccard 5-grammes) médiane 0,000, max 0,089, aucune paire
  ≥ 0,30 ; 188 ouvertures de `reason` distinctes sur 200. Les raisonnements sont écrits un par un.
- **Encodage impeccable** : zéro caractère de contrôle, zéro espace insécable parasite, zéro id dupliqué.
- **Zéro bloc de code réutilisé entre splits** côté `CODE_ANALYSIS` : la fuite est spécifique au RAG.
- Aucune famille à cheval sur le split ; composition du golden set exactement conforme aux cibles.

## Limites de l'audit

- La **justesse de fond des étiquettes** n'a pas été évaluée — un `check` est-il correct au regard du code ?
  Cela demanderait de rejuger les 200 exemples. C'est l'objet de la relecture humaine (`REVUE_GOLDEN.md`),
  qui reste entière.
- Aucun entraînement ni inférence n'a été lancé : l'effet réel des raccourcis sur le juge fine-tuné est une
  inférence tirée de la structure des données, pas une mesure sur modèle.
- Compte exact des exemples dépassant 1024 tokens non calculé.

## Plan de reprise retenu

Décision du 2026-09-15 : **reprise ciblée avant tout fine-tuning**.

| # | Chantier | Cible | État |
|---|---|---|---|
| 1 | Purge `Synthèse : cas limite.` | 40 cibles, 1 tournure, substitution mécanique | ✅ fait |
| 2 | Étiquettes `verbeux` fausses | `b13-007`, `b14-008` | ✅ fait |
| 3 | Revendications d'exécution | 104 occurrences, 61 tournures — reformulation cas par cas | à faire |
| 4 | Longueur, `CODE_ANALYSIS` | 38 FAIL sous 666 car., surtout `generation` / `refactoring` / `question_reponse` | à faire |
| 5 | Longueur, `RAG_FAITHFULNESS` | 8 FAIL sous 410 car., face à 14 PASS de médiane 733 | à faire |
| 6 | Polarité `citations_exactes` | produire la famille « citation déformée », absente du corpus | à faire |
| 7 | Contextes RAG du golden | contextes inédits pour les items de test ; regrouper par contexte les familles qui le partagent | à faire |
| 8 | Verbeux corrects | 13 au lieu des 15 exigés, conséquence de la correction n°2 | à faire |

Le chantier 8 découle du 2 : `b13-007` et `b14-008` étaient comptés à tort parmi les verbeux corrects. La
cible de 15 n'a donc **jamais** été réellement atteinte ; il manque deux exemples verbeux et corrects, à
produire de préférence en `parfait` — sur les 13 restants, 11 sont des `limite`, ce qui déséquilibre le
contrôle inverse du test de verbosité.

Le chantier 7 doit aussi corriger un effet de bord visible : quatre exemples partageant le contexte
`CTX_LUCENE_COMBINE` vivent sous quatre familles distinctes, et l'un d'eux garde un nom de famille
trompeur (`rag-combinaison-sources-lucene-verbeux`, alors qu'il n'est plus étiqueté verbeux).

Principe directeur des chantiers 4 et 5 : allonger les FAIL, jamais raccourcir les PASS. Une réponse
**verbeuse et fausse** est exactement le cas difficile que le juge doit apprendre à démasquer — le remède
va donc dans le sens de l'objectif au lieu de le contrarier.
