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
| 4 | Longueur, `CODE_ANALYSIS` | 38 FAIL sous 666 car., surtout `generation` / `refactoring` / `question_reponse` | ✅ **clos** — 26 réécrits, voir ci-dessous |
| 5 | Longueur, `RAG_FAITHFULNESS` | 8 FAIL sous 410 car., face à 14 PASS de 666 à 1087 | ✅ clos — 84,0 % → 76,0 % (p 0,006 → 0,076), voir ci-dessous |
| 6 | Polarité `citations_exactes` | produire la famille « citation déformée », absente du corpus | à faire |
| 7 | Contextes RAG du golden | contextes inédits pour les items de test ; regrouper par contexte les familles qui le partagent | ✅ clos — fuite 9/11 → **0/12**, voir ci-dessous |
| 8 | Verbeux corrects | 13 au lieu des 15 exigés, conséquence de la correction n°2 | ✅ clos — cible ramenée à 13, voir ci-dessous |

Le chantier 8 découle du 2 : `b13-007` et `b14-008` étaient comptés à tort parmi les verbeux corrects. La
cible de 15 n'a donc **jamais** été réellement atteinte.

**Décision du 2026-09-15 : la cible est ramenée à 13, et le chantier est clos sans production.** Les
candidats à une promotion en verbeux sont longs — 1295 à 1635 caractères — mais comptent **zéro section**
et ne présentent ni préambule ni digression finale : ils sont étoffés, pas verbeux. Les réétiqueter
reproduirait exactement l'erreur trouvée sur `b13-007` et `b14-008`, en sens inverse. Et les rendre
verbeux supposerait de **rembourrer délibérément deux réponses correctes** pour satisfaire un compteur,
c'est-à-dire d'employer le mécanisme même qui a produit le biais de longueur que les chantiers 4 et 5
viennent de retirer. Un compteur atteint par un procédé que le corpus condamne ne vaut pas mieux qu'un
compteur manqué.

## Clôture du chantier 7 — une famille par contexte d'extraction

Le diagnostic tenait en un chiffre : **50 exemples RAG pour seulement 20 contextes d'extraction
distincts**, chacun décliné sous une famille différente. Le mécanisme anti-fuite du split, qui groupe par
`famille`, ne pouvait donc rien empêcher — il séparait allègrement des exemples bâtis sur le même
contexte récupéré. Le golden set en portait la trace : 9 items sur 11 avec un contexte déjà vu en
entraînement, 8 avec contexte **et** requête identiques, et trois paires de jumeaux à l'intérieur même du
golden (`b14-006`/`b14-020`, `b12-004`/`b12-009`, `b13-002`/`b13-010`).

Correction : **une famille par contexte**, ce qui est ce que le champ `famille` était censé désigner
depuis le début — un scénario, pas une rédaction. Les 50 exemples RAG passent de 50 familles à 20, de
tailles 1 (×6), 2 (×2), 3 (×8) et 4 (×4). Aucun contenu n'a été écrit ni modifié, seul `meta.famille`
change, ce qui laisse les étiquettes, les longueurs et les tests de permutation intacts.

| | avant | après |
|---|---|---|
| Familles RAG | 50 | **20** |
| Golden : contexte déjà vu en entraînement | 9 / 11 | **0 / 12** |
| Golden : contexte **et** requête déjà vus | 8 / 11 | **0 / 12** |

**La garantie est structurelle, pas fortuite.** Un balayage de 17 graines de tirage donne une fuite nulle
sur les 17 : dès lors qu'une famille se déplace en bloc, aucun tirage ne peut placer deux exemples du même
contexte de part et d'autre. C'est vérifié graine par graine, pas déduit.

Conséquence assumée : le tirage change de nature, et la graine 3 — choisie pour une structure en
singletons — n'a plus de sens. Elle donnait 4 items de fidélité RAG sur 50 ; la graine 11, retenue après
balayage, en donne 6. Le critère de départage a été la couverture de `RAG_FAITHFULNESS` plutôt que l'écart
global aux cibles, ces items étant le seul instrument de surveillance de la posture monde fermé.

Le chantier 7 doit aussi corriger un effet de bord visible : quatre exemples partageant le contexte
`CTX_LUCENE_COMBINE` vivent sous quatre familles distinctes, et l'un d'eux garde un nom de famille
trompeur (`rag-combinaison-sources-lucene-verbeux`, alors qu'il n'est plus étiqueté verbeux).

Principe directeur des chantiers 4 et 5 : allonger les FAIL, jamais raccourcir les PASS. Une réponse
**verbeuse et fausse** est exactement le cas difficile que le juge doit apprendre à démasquer — le remède
va donc dans le sens de l'objectif au lieu de le contrarier.

## Clôture du chantier 4 — et une erreur de méthode dans ma propre mesure

26 FAIL `CODE_ANALYSIS` ont été réécrits sur les lots 02 à 07, défauts reconduits mot pour mot et
étiquettes vérifiées inchangées à chaque lot. Deux corrections successives de l'instrument ont été
nécessaires avant de pouvoir conclure, et toutes deux invalidaient des chiffres que j'avais annoncés.

**Première correction — la direction.** La statistique ne balayait que « long ⇒ PASS ». Après six lots,
la médiane FAIL est passée au-dessus de la médiane PASS et le raccourci a changé de camp : « court ⇒ PASS »
l'emportait à 60,0 % contre 59,3 %. Toutes mes réécritures avaient atterri entre 1200 et 1850 caractères
alors que les PASS vivent entre 700 et 1400 : j'avais construit un amas de FAIL très longs. Le principe
« allonger les FAIL » était donc trop grossier — la cible n'est pas « long », c'est que les **deux
distributions se recouvrent**.

**Seconde correction — le plancher de bruit.** Je comparais une statistique **maximisée** (meilleur seuil
parmi 145, dans deux directions) à un simple taux de base. C'est invalide : maximiser sur ~290 hypothèses
gonfle le résultat même sur des données sans information. Le test de permutation, 3000 tirages des verdicts
contre les longueurs réelles, donne une **moyenne nulle de 57,4 %** et un p95 à **61,3 %**.

| État | Statistique | z | Verdict |
|---|---|---|---|
| Avant reprise | 75,3 % | **+8,8** | signal réel et massif |
| Après lots 02-04 | 66,7 % | +4,6 | signal réel |
| Après lots 05-07 | 60,0 % | **+1,3** | **bruit** (p = 0,132) |

**Conséquence opérationnelle : les 14 FAIL courts restants ne doivent pas être réécrits.** La simulation
le montrait déjà — les porter à la médiane des PASS faisait *monter* la statistique à 64,0 %, les répartir
sur les quantiles à 62,7 % — et le test de permutation explique pourquoi : ces exemples courts sont
désormais la seule chose qui peuple le bas de la distribution côté FAIL, donc la seule qui retienne le
raccourci inversé. Il n'y a plus de signal à supprimer.

**À retenir pour la suite du projet** : tout seuil choisi a posteriori doit être comparé à une distribution
nulle par permutation, jamais à un taux de base. Cette règle vaut aussi pour les métriques du benchmark.

### Le même test, tâche par tâche

Appliqué séparément à chaque posture, il montre que le défaut n'était pas uniforme — et que le chantier 5
reste pleinement justifié :

| Tâche | n | Observé | Nulle (moy / p95) | z | p | Verdict |
|---|---|---|---|---|---|---|
| `CODE_ANALYSIS` | 150 | 60,0 % | 57,4 / 61,3 % | +1,3 | 0,132 | bruit — chantier clos |
| `RAG_CONTEXT_RELEVANCE` | 25 | 60,0 % | 65,8 / 76,0 % | **−1,1** | 0,983 | sous le hasard, rien à faire |
| `RAG_FAITHFULNESS` | 25 | **84,0 %** | 66,4 / 76,0 % | **+3,5** | **0,006** | **signal réel** |

Noter au passage l'ampleur du plancher de bruit à n = 25 : la statistique maximisée atteint 66 % en moyenne
et 76 % au p95 sur des verdicts tirés au hasard. Un « 76 % » brut sur un sous-ensemble de cette taille ne
veut donc strictement rien dire. C'est la même erreur de lecture qui m'a fait poursuivre le chantier 4 bien
après sa fin utile.

**Cible chiffrée du chantier 5.** Les 8 FAIL concernés (`b13-010` 246, `b14-015` 283, `b12-014` 289,
`b13-012` 292, `b12-009` 324, `b13-014` 342, `b14-014` 357, `b14-017` 404) doivent rejoindre la plage des
PASS, **666 à 1087 caractères**, sans la dépasser. Viser « long » plutôt que la distribution des PASS est
précisément ce qui a retourné le biais côté code ; l'erreur ne doit pas être refaite ici.

## Clôture du chantier 5 — l'erreur a pourtant été refaite

Le paragraphe ci-dessus a été écrit, puis ignoré au tour suivant. Sur les 8 réécritures, **7 sont sorties
de la plage**, entre 1144 et 1470 caractères, et la statistique est passée de 84,0 % à **88,0 %**
(p 0,001) : le corpus était devenu **pire qu'avant le chantier**. La médiane FAIL grimpait à 1196 pour une
médiane PASS de 734, les deux distributions étant à nouveau presque disjointes, simplement dans l'autre
sens.

La cause n'est pas l'ignorance de la règle, elle était écrite. C'est d'avoir rédigé au jugé — « ajouter
quelques sections » — sans mesurer la longueur obtenue avant de régénérer. **Une consigne écrite ne
remplace pas une mesure ; il faut vérifier la sortie, pas l'intention.**

Correction par raccourcissement des 7 exemples, avec des cibles étalées sur 690-1080 pour entrelacer les
deux distributions plutôt que de les séparer :

| Étape | Observé | z | p |
|---|---|---|---|
| Avant chantier 5 | 84,0 % | +3,5 | 0,006 |
| Après surcorrection | 88,0 % | +4,3 | 0,001 |
| Après raccourcissement | **76,0 %** | **+2,0** | **0,076** |

État final : 9 des 11 FAIL dans la plage des PASS, deux la dépassant de 43 et 84 caractères, étiquettes
toutes intactes.

**Deux réserves à ne pas masquer.** D'abord, p = 0,076 est **marginal** : la valeur observée tombe
exactement sur le p95 de la distribution nulle. Ce n'est pas un résultat net, c'est le franchissement
d'un seuil conventionnel. Ensuite, les longueurs cibles ont été **choisies** parmi plusieurs scénarios
simulés ; optimiser des données contre la statistique qui les mesure, puis présenter cette statistique
comme preuve, serait circulaire. Le scénario le plus « favorable » testé donnait d'ailleurs 56 %, soit
z = −1,8, c'est-à-dire des longueurs anormalement bien appariées — il a été écarté pour cette raison.
Le critère retenu est le recouvrement des distributions, pas la maximisation de p.

À n = 25, avec un plancher de bruit à 66 % et un p95 à 76 %, il faut de toute façon considérer que cette
tâche ne permet aucune conclusion fine sur la longueur.
