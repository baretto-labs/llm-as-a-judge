# Pré-enregistrement du protocole de mesure

**Date : 2026-09-17.** Rédigé **avant** tout entraînement et avant toute exécution du benchmark.
Aucun résultat de modèle n'était disponible au moment de l'écriture.

Ce document fixe la métrique principale, les tests, et surtout **ce qui sera déclaré non concluant**.
Il existe pour une raison précise : après plusieurs semaines de travail sur ce corpus, l'auteur comme le
relecteur souhaiteront que le fine-tuning l'emporte. Les règles sont donc arrêtées pendant qu'il est
encore possible d'être impartial.

Précédent qui justifie cette précaution : au cours de la construction du corpus, un biais de verbosité a
été « mesuré » en balayant 145 seuils et deux directions, puis comparé à un taux de base. L'écart paraissait
valoir +8,8 écarts-types. Un test de permutation a montré qu'il en valait +1,3, soit du bruit (p = 0,132).
Le défaut n'était pas dans les chiffres mais dans le choix de l'analyse après coup.

---

## 1. Gel du corpus

Le corpus est **gelé à la date de ce document** : 200 exemples, 0 erreur de validation, 104 PASS / 96 FAIL,
golden set de 50 items tiré avec `SPLIT_SEED=11`.

Toute modification ultérieure du corpus invalide ce pré-enregistrement et impose d'en dater un nouveau.
Seule exception admise : une correction d'erreur factuelle découverte pendant la relecture par paire, qui
devra être consignée dans `data/REVUE_GOLDEN.md` avec sa date, et signalée dans le REX.

## 2. Ce qui est déjà connu, et ne sera donc pas présenté comme une découverte

- Le corpus porte trois biais mesurés puis corrigés, documentés dans `AUDIT.md`.
- Une fuite déterministe « consigne facultative ⇒ PASS » valait 17/17 ; elle a été ramenée à 17/30 sur le
  corpus et 3/6 sur le golden set.
- Les tests de permutation sur la verbosité sont tous dans le bruit.
- La relecture par paire couvre 12 items sur 50 à ce jour, avec 11/12 d'accord sur le verdict au premier
  passage et 2 désaccords au niveau contrôle.

## 3. Variantes figées

Aucune variante ne sera ajoutée ni retirée après cette date.

| variante | nature |
|---|---|
| `14B-baseline-nu` | modèle de base, invite système minimale |
| `14B-baseline-conventions` | modèle de base, **conventions du corpus explicitées dans l'invite** |
| `14B-finetuned` | adaptateur LoRA |
| `32B-baseline-conventions` | modèle de base, conventions dans l'invite |
| `32B-finetuned` | adaptateur LoRA |
| `gemini-flash` | hébergé, version épinglée et datée |
| `gemini-pro` | hébergé, version épinglée et datée |

**`14B-baseline-conventions` est le concurrent sérieux du fine-tune, et non `14B-baseline-nu`.** Comparer
un fine-tune à un modèle privé du règlement intérieur qu'on lui a appris serait un homme de paille. Les
conventions écrites dans l'invite sont celles de `PROTOCOLE.md` : consigne facultative non bloquante,
portée de `citations_exactes`, contrôle dédié qui ne double-compte pas avec `respect_consignes`,
règle PASS ⟺ tous les contrôles vrais.

## 4. Métrique principale

**Justesse stricte du verdict sur les 50 items du golden set** : proportion d'items pour lesquels le
verdict rendu (`PASS` / `FAIL`) est identique à l'étiquette de référence.

Une seule métrique principale. Toutes les autres sont secondaires et déclarées comme telles en §6.

## 5. Comparaison principale et test

**Comparaison principale : `14B-finetuned` contre `14B-baseline-conventions`.** C'est elle qui porte
l'affirmation « le fine-tuning améliore la qualité du juge ».

- **Test** : McNemar exact (binomial bilatéral sur les paires discordantes), α = 0,05.
- **Intervalle** : bootstrap apparié par percentiles, 10 000 rééchantillonnages, sur la différence de
  justesse.
- Les deux variantes jugent exactement les mêmes items : le test apparié est donc le bon, et deux
  intervalles indépendants seraient une erreur.

### Puissance, estimée avant les résultats

Avec n = 50 items appariés, l'étude ne peut détecter que des effets importants :

- une différence d'environ **15 points ou plus** sera détectée avec une puissance raisonnable ;
- une différence de **10 points ou moins** ne le sera pas, et sera rapportée comme non concluante ;
- l'intervalle sur la différence fera approximativement **±12 à 14 points** autour de 90 % de justesse.

Cette limite est structurelle et connue d'avance. Elle sera énoncée dans le REX, y compris si le résultat
est favorable.

## 6. Métriques secondaires

Déclarées secondaires par avance. **Aucune ne pourra être promue en métrique principale après coup**,
quel que soit le résultat de la principale.

1. Taux de sortie conforme au schéma (JSON analysable, clés requises présentes).
2. Taux de cohérence interne (`verdict == PASS` ⟺ tous les contrôles vrais).
3. Accord moyen contrôle par contrôle.
4. Justesse sur la seule strate `limite`, où se concentre la difficulté.
5. Auto-cohérence : même entrée rejouée sur plusieurs passes, taux de verdicts identiques.
6. Latence et coût par jugement.

## 7. Règle de conclusion, arrêtée d'avance

| résultat | ce qui sera écrit |
|---|---|
| p < 0,05 **et** intervalle excluant 0 | « le fine-tuning améliore la justesse de X points, IC [a, b] » |
| intervalle contenant 0 | « **non concluant** » — avec la largeur de l'intervalle et le rappel que l'étude ne pouvait pas détecter moins de ~15 points |
| différence négative | publiée telle quelle, sans atténuation |

**Engagement explicite : un résultat défavorable au fine-tuning sera publié avec la même visibilité qu'un
résultat favorable.** Si le fine-tuning n'apporte rien, le REX le dira.

Formulation interdite : « tendance à l'amélioration », « amélioration non significative mais encourageante »,
et toute variante visant à sauver un intervalle qui contient zéro.

## 8. Instrumentation du coût

À mettre en place **avant** le premier entraînement, faute de quoi les chiffres sont perdus.

- **Entraînement** : durée mesurée, mémoire de pointe, nombre d'itérations et de jetons vus, spécification
  de la machine (Apple M3 Pro, 36 Go).
- **Inférence locale** : jetons entrée/sortie, durée par item, mémoire de service.
- **Inférence hébergée** : jetons facturés, tarif à la date d'exécution, coût total du benchmark.

Le coût ne sera **pas** présenté comme un verdict « moins cher », mais comme un **volume d'équilibre** :
en dessous de N jugements par mois, l'hébergé revient moins cher ; au-dessus, le local. Le lecteur applique
son propre N.

## 9. Limites connues, à publier

1. **Provenance de la vérité de référence.** Les 200 étiquettes ont été rédigées par un LLM (Claude) puis
   validées par un humain sur un sous-ensemble du golden set. Le κ inter-annotateur issu de
   `data/REVUE_GOLDEN.md` sera publié avec son intervalle, ainsi que le nombre exact d'items relus. C'est la
   limite la plus sérieuse de l'étude, et elle pèse particulièrement sur la comparaison avec un juge
   extérieur au corpus.
2. **Taille de l'échantillon.** 50 items, d'où la puissance limitée énoncée en §5.
3. **Reproductibilité asymétrique.** Un adaptateur LoRA est figé et rejouable ; une API hébergée évolue.
   Les chiffres Gemini valent à leur date et ne seront pas reproductibles à l'identique.
4. **Domaine unique.** Assistant de code, majoritairement Java, Python, TypeScript et SQL. Aucune
   généralisation à d'autres domaines ne sera revendiquée.
5. **Un seul tirage.** `SPLIT_SEED=11`, sans validation croisée.

## 10. Ce qui n'est pas pré-enregistré

Toute analyse non listée ici est **exploratoire** et sera signalée comme telle dans le REX, sans test de
signification présenté comme confirmatoire. Cela vaut notamment pour la comparaison entre tailles
(14B contre 32B), dont il est établi d'avance qu'elle manque de puissance : elle sera rapportée en section
secondaire, et « indistinguables » y est un résultat acceptable et attendu.

---

## Addendum daté — 2026-09-17, après signature

Ajout **additif** à la section §9 « Limites connues ». Aucune métrique, aucun test et aucune règle de
conclusion n'est modifié : seule une limite découverte après signature est consignée.

### 6. Items RAG corrélés par contexte partagé

Le golden set compte **12 items RAG reposant sur seulement 5 contextes d'extraction distincts**.
Un même contexte y sert jusqu'à trois items, sous des marqueurs de tâche différents
(`RAG_CONTEXT_RELEVANCE` et `RAG_FAITHFULNESS`).

C'est la conséquence directe et voulue du regroupement par famille, qui fait voyager les familles en bloc
dans le tirage et rend structurellement impossible la fuite de contexte entre entraînement et test. Le
prix en est une **corrélation entre items de test** : un juge qui comprend un contexte marque sur tous les
items qui en dépendent, et un juge qui s'y trompe les perd tous ensemble.

**Conséquence sur la puissance :** la taille d'échantillon effective des items RAG est inférieure à leur
nombre. Les intervalles calculés sur la sous-population RAG seront donc **optimistes**, et seront présentés
comme tels. La métrique principale portant sur les 50 items, majoritairement `CODE_ANALYSIS`, l'effet sur
elle reste limité — mais il n'est pas nul et ne sera pas passé sous silence.

**Conséquence sur la relecture par paire :** deux items d'une même famille ne peuvent pas constituer deux
points de mesure indépendants. L'analyse du premier règle le second. Les items concernés sont signalés
comme compromis dans `data/REVUE_GOLDEN.md`.

---

## Addendum daté — 2026-09-19, révision du critère de fuite de surface

Ajout **additif**. La métrique principale, la comparaison principale, le test et la règle de conclusion
sont inchangés. Seul le critère interne d'acceptation du corpus est révisé, et le motif est consigné.

### Le critère initial était mal posé

Il avait été fixé à « balayage global p ≥ 0,05 et aucune strate déterministe ». Trois tours de correction
ont montré que la première moitié est une cible sans fin : sur un corpus écrit par un seul auteur, il
subsiste toujours un corrélat de forme, et neutraliser un trait fait remonter le suivant de la même
famille — sections, titres, tableaux, gras sont quatre mesures d'une seule habitude de rédaction.

### Critère retenu à la place

**Aucune cellule déterministe**, c'est-à-dire aucune règle de surface à zéro contre-exemple. La
distinction est de nature, non de degré : une corrélation laisse au modèle une raison d'apprendre autre
chose, une règle sans exception ne lui en laisse aucune.

**État atteint :** plus aucune cellule déterministe sur les traits balayés. `reponse_tableau` passe de
0 PASS / 18 FAIL à 5P/2F en non verbeux et 4P/16F en verbeux ; `reponse_sections` de 0P/24F à une
répartition mêlée. `reponse_gras` mène désormais `CODE_ANALYSIS` à 64,7 % (p = 0,0225) mais n'est **pas**
déterministe — 48P/17F contre 21P/31F — et n'est donc pas traité.

### Ce qui remplace la poursuite du nettoyage

Conformément à la pratique documentée en 2026 sur le biais de format des juges, la fuite résiduelle est
**mesurée et publiée** plutôt que poursuivie :

1. **Passe « format normalisé »** ajoutée aux métriques secondaires : le benchmark est rejoué sur des
   réponses dépouillées de leur Markdown — titres, puces, gras, tableaux — et **l'écart entre les deux
   passes mesure la part de forme dans le score du juge**.
2. **Exclusion obligatoire** de cette passe : les 5 items dont la requête impose un format, où la forme
   *est* le critère évalué et dont le dépouillement les rendrait injugeables.
3. Le chiffre de fuite résiduelle du corpus est publié tel quel dans le REX.

### Pourquoi ce renversement

Le nettoyage est non borné, il dégrade la représentativité du corpus, et un corpus déclaré « propre » ne
prouve rien. Un écart mesuré entre passe formatée et passe dépouillée est vérifiable, reproductible, et
constitue une **preuve positive** que le juge a appris autre chose que la forme.

---

## Gel du corpus — 2026-09-19

Le corpus est **gelé** à cette date, conformément au §1. Dernier état :

```
200 exemples, 0 erreur de validation, 104 PASS / 96 FAIL
golden 50 (24 PASS / 26 FAIL), SPLIT_SEED=11
aucune cellule de surface déterministe
```

Les splits ont été régénérés après les dernières retouches de contenu : `train` 135, `valid` 15,
`golden` 50, avec 27 exemples portant un tableau répartis sur les trois. Les verdicts et les `cas`
n'ayant jamais bougé, la partition est restée identique d'un bout à l'autre des corrections — le tirage,
le golden set et les 21 relectures déjà faites demeurent valides.

**Premier entraînement lancé après ce gel.** Toute modification ultérieure du corpus invalide les
résultats produits et impose un nouveau pré-enregistrement daté.

---

## Addendum daté — 2026-09-20, choix du point de contrôle

Ajout **additif**, rédigé **avant toute exécution du benchmark**. La métrique principale, la comparaison
principale, le test et la règle de conclusion sont inchangés.

### Ce que l'entraînement a montré

La perte de validation atteint son minimum à **1,104 à l'itération 250**, puis remonte — 1,207 à 300,
1,201 à 350, 1,183 à 400 — tandis que la perte d'entraînement continue de descendre jusqu'à 0,587.
Surapprentissage modéré : même au point le plus surappris, la validation reste à **-35 %** par rapport à
l'itération 1 (1,816). Les points de contrôle étant sauvegardés toutes les 100 itérations, il n'en existe
aucun à 250.

### Décision

**Deux variantes sont benchmarkées, et leur statut est fixé ici, avant de connaître leurs résultats.**

| variante | point de contrôle | val loss | statut |
|---|---|---|---|
| `14B-finetuned` | `0000200_adapters.safetensors` | 1,126 | **principale** — porte la métrique principale |
| `14B-finetuned-final` | `0000400_adapters.safetensors` | 1,183 | **secondaire, exploratoire** |

`14B-finetuned` est sélectionné sur la **perte de validation**, jamais sur le golden set : c'est la
fonction même du jeu de validation, et la pratique standard.

`14B-finetuned-final` est ce qu'obtient quiconque lance `make train-14b` sans regarder la courbe —
`adapters.safetensors` pointe dessus. Il est rapporté pour chiffrer **le coût de ne pas surveiller sa
validation**, sur la même tâche et le même jeu de test.

### Interdictions explicites

- **`14B-finetuned-final` ne pourra jamais être promu en variante principale**, quel que soit son score.
- Il est **interdit** de comparer les deux sur le golden set puis de désigner la meilleure comme
  principale. Toute la légitimité de cette double mesure tient à l'ordre des opérations, et cet ordre est
  consigné ici, horodaté, avant la première exécution.
- Si `14B-finetuned-final` devait obtenir un meilleur score que `14B-finetuned`, ce résultat serait publié
  tel quel, comme un fait contre-intuitif, sans réattribution de statut.

### Attendu déclaré d'avance

L'écart de perplexité entre les deux vaut 7 %. Sur 50 items et une métrique de verdict, cela représente
vraisemblablement **zéro à trois items**, soit largement à l'intérieur de l'intervalle de ±12 à 14 points
annoncé au §5. Il est donc probable que les deux variantes soient **indistinguables**, et ce résultat-là
sera rapporté comme tel.

---

## Amendement daté — 2026-09-20, liste des variantes et texte des conventions

Le §3 interdit d'ajouter ou de retirer une variante après signature. Cet amendement l'exerce
explicitement plutôt que de modifier la liste en silence.

### Gemini est retiré de la liste, faute de clé d'API

`gemini-flash` et `gemini-pro` **ne sont pas benchmarkés**. Motif : aucune clé d'API disponible à cette
date. Ce n'est pas un retrait motivé par un résultat — aucune exécution n'a eu lieu.

**Condition de réintégration :** leur ajout ultérieur exigera un **nouvel amendement daté, antérieur à
toute exécution les concernant**, et ils seront alors rapportés comme variantes ajoutées après coup, avec
leur date. Un juge extérieur introduit après avoir vu les résultats locaux n'aurait aucune valeur
probante.

**Conséquence sur la portée :** la limite §9.1 — provenance de la vérité de référence — perd de son
acuité immédiate, puisqu'aucun juge extérieur au corpus n'est mesuré. Elle reste entière pour le REX, et
redeviendra critique le jour où Gemini entrera.

### Liste des variantes effectivement mesurées

| variante | modèle servi | adaptateur | statut |
|---|---|---|---|
| `14B-baseline-nu` | 14B-4bit | aucun | secondaire — montre l'écart dû au seul prompt |
| `14B-baseline-conventions` | 14B-4bit | aucun | **concurrent de la comparaison principale** |
| `14B-finetuned` | 14B-4bit | `adapters/14b-judge-200` | **principale** (point 200, val 1,126) |
| `14B-finetuned-final` | 14B-4bit | `adapters/14b-judge` | secondaire (point 400, val 1,183) |
| `32B-baseline-conventions` | 32B-4bit | aucun | exploratoire |
| `32B-finetuned` | 32B-4bit | `adapters/32b-judge` | exploratoire, sous réserve de faisabilité en 36 Go |

### Texte des conventions injectées dans l'invite

Les variantes `*-baseline-conventions` reçoivent les règles de `PROTOCOLE.md` **mot pour mot**, sans
ajout, sans reformulation et sans exemple. Décision prise avant toute exécution : un texte enrichi ferait
de la ligne de base un mode d'emploi que le fine-tune n'a jamais reçu, un texte appauvri en ferait un
homme de paille. La copie littérale est le seul choix défendable, et elle est vérifiable.

### Défaut d'appariement corrigé avant toute mesure

`build_report` **devinait** les paires à comparer par `size` et `fine_tuned`, et prenait le premier
élément trouvé dans l'ordre du fichier. Avec quatre variantes 14B — deux non fine-tunées, deux
fine-tunées — la comparaison principale déclarée aurait pu être remplacée silencieusement par
`14B-finetuned-final` contre `14B-baseline-nu`, soit le point surappris contre l'homme de paille, avec un
intervalle de confiance d'apparence normale.

**Les paires sont désormais déclarées explicitement dans `configs/variants.json`**, et le script doit
échouer bruyamment si une variante nommée est absente. Aucune mesure ne sera produite avant ce correctif.

---

## Amendement daté — 2026-09-20, correction de huit étiquettes `respect_consignes`

Le §1 gèle le corpus et impose qu'une modification ultérieure soit datée et signalée. Cet amendement
l'exerce. **Aucune exécution du benchmark n'a eu lieu** : la correction est antérieure à toute mesure.

### Ce qui a été découvert, et comment

Pendant la relecture, l'annotateur a marqué `respect_consignes` à V sur `b06-008` là où l'étiquette le
mettait à F. En vérifiant, l'auteur des étiquettes a constaté que **sa propre étiquette contredisait la
convention qu'il avait lui-même défendue la veille** — « un contenu faux n'est pas une consigne non
suivie ». L'annotateur avait raison, l'étiquette avait tort.

Un audit des 17 items portant `respect_consignes = faux` a suivi. **Huit étaient incohérents** avec la
convention : `b03-005`, `b06-008`, `b04-006`, `b05-004`, `b05-007`, `b06-002`, `b06-004`, `b08-009`.
Leur requête ne formule aucune exigence explicite — elle dit « explique et corrige », « simplifie »,
« écris une fonction qui… ». La réponse a fait la chose, mal : cela relève des contrôles 1 et 2.

**Neuf conservent `respect_consignes = faux`**, chacun violant une exigence littéralement écrite dans
l'énoncé : détection « à l'exécution » (`b09-006`), définition de l'identité sur deux composants
(`b10-003`), « y compris les auteurs qui n'en ont aucun » (`b02-006`), « sans changer le comportement »
(`b03-006`), « une nouvelle configuration sans modifier celle reçue » (`b04-007`), bornes jusqu'à
`Integer.MAX_VALUE` (`b05-002`), « sans lui révéler qu'elle existe » (`b05-014`), validation d'un entier
strictement positif (`b03-001`), et « empêche l'appelant de modifier la liste » (`b04-002`).

**Deux items ont été retirés de la liste des corrections après examen du code source.** `b03-001` et
`b04-002` figuraient dans la classification initiale, que l'annotateur avait validée ; la lecture de leur
`<thinking>` a montré qu'ils invoquaient une exigence réellement explicite. Le changement a été signalé à
l'annotateur plutôt qu'appliqué en silence.

### Effets vérifiés

- **Aucun verdict ne change.** Sur les 17 items, aucun n'avait `respect_consignes` comme seul contrôle
  faux : PASS ⟺ tous les contrôles vrais ne bascule nulle part.
- **Aucun `cas` ne change** — 80 `parfait` / 80 `defaillant` / 40 `limite` — donc le tirage
  `SPLIT_SEED=11` est identique, le golden set est identique, et **les 28 relectures déjà faites restent
  valides**.
- Deux `<thinking>` ont été réécrits, `b03-005` et `b05-007`, qui adossaient explicitement le défaut à la
  consigne et auraient contredit un contrôle passé à V.
- Corpus : 200 exemples, 0 erreur, PASS 104 / FAIL 96, golden 24/26.

### Conséquence coûteuse, assumée

**Six des huit corrections touchent le jeu `train`.** L'adaptateur `adapters/14b-judge`, entraîné le
2026-09-19, l'a été sur des étiquettes désormais fausses : **il est périmé et l'entraînement est relancé**.
Les points de contrôle antérieurs, y compris le `0000200` déclaré principal, sont invalidés par la même
cause et seront régénérés.

Les décisions de l'addendum du 2026-09-20 sur le choix du point de contrôle — variante principale
sélectionnée sur la perte de validation, variante finale rapportée en secondaire — **restent en vigueur et
s'appliqueront au nouvel entraînement**, avec les nouvelles valeurs de validation.

---

## Amendement daté — 2026-09-20, ambiguïté assumée du contrôle `respect_consignes`

Déclaré **avant toute exécution du benchmark**. Ne modifie ni la métrique principale, ni la comparaison
principale, ni le test, ni la règle de conclusion. Fixe la manière dont un artefact connu sera rapporté.

### Le fait établi

Le libellé du contrôle 3 est : « Toutes les consignes obligatoires de la requête sont respectées. » La
convention du corpus lui donne un sens **étroit** — seules comptent les exigences explicitement formulées
au-delà de la tâche elle-même : format imposé, contrainte de dépendance, signature figée, définition
donnée. **Le texte ne l'énonce pas.**

Mesuré sur les 14 items relus où ce contrôle était en jeu :

| la requête porte… | accord annotateur humain / étiquette |
|---|---|
| une exigence littérale | **7 / 7** |
| aucune exigence littérale | **1 / 7** |

Un lecteur attentif, appliquant le sens ordinaire du français, juge donc `respect_consignes` faux dès que
la réponse échoue à sa tâche. Ce n'est pas une erreur de l'annotateur : c'est la lecture du texte.

### Décision : le libellé est conservé

Réécrire la rubrique aurait imposé de régénérer les 200 exemples et de relancer l'entraînement. Surtout,
cela aurait **retiré au fine-tuning une partie de ce qu'il apporte réellement** : l'acquisition d'une
convention maison non écrite est précisément la fonction d'un fine-tuning, et c'est ce que les lecteurs du
REX cherchent à savoir.

### Engagements de rapport, pris d'avance

1. **La table de contingence ci-dessus sera publiée**, comme mesure directe de l'ambiguïté.
2. **La part du gain attribuable à l'apprentissage de la convention sera nommée explicitement**, et non
   présentée comme une supériorité de jugement. Formulation interdite : laisser entendre que le fine-tune
   « juge mieux » là où il applique seulement une règle que la rubrique n'énonce pas.
3. **`14B-baseline-nu` sera rapporté avec la réserve correspondante** : ne recevant que la rubrique, il
   subit l'ambiguïté et son score sur le contrôle 3 ne mesure pas sa qualité de jugement.
4. **`14B-baseline-conventions` reste le concurrent de la comparaison principale**, précisément parce que
   les conventions de `PROTOCOLE.md` figurent dans son invite : il est protégé de l'artefact, ce qui rend
   la comparaison principale interprétable.
5. L'accord par contrôle sera publié **avec et sans le contrôle 3**, afin que le lecteur puisse isoler
   l'effet de l'ambiguïté sur les chiffres.

---

## Amendement daté — 2026-09-20, correction de l'étiquette `b03-001`

Neuvième étiquette corrigée depuis le gel, **avant toute exécution du benchmark**.

`exactitude_technique` passe de V à F. Motif : la réponse conclut par « la fonction est générique et
compile en mode strict », affirmation littéralement vraie mais servant de quitus à un code dont le
découpage est faux dès la deuxième tranche. Relevé par l'annotateur humain ; le raisonnement de référence
listait les affirmations explicites sans examiner la portée de cette conclusion.

**Effets vérifiés :** verdict FAIL inchangé, `cas` inchangé, invariants intacts (200 exemples,
104 PASS / 96 FAIL, 80/80/40, golden 24/26). **`b03-001` appartient au golden set et non à `train`** :
l'entraînement lancé ce jour n'est pas affecté et se poursuit.

Troisième correction d'étiquette à l'initiative de l'annotateur, après `b09-009` et `b06-008` — fait à
rapporter dans le REX comme mesure de ce que la relecture humaine apporte réellement au-delà du κ.

---

## Amendement daté — 2026-09-20, correction de verdict sur `b13-004`

Dixième étiquette corrigée depuis le gel, **avant toute exécution du benchmark**, et **la première qui
change un verdict**.

`contexte_suffisant` passe de V à F, donc le verdict de PASS à FAIL et `cas` de `parfait` à `defaillant`.
Motif : le contexte ne contient que des signatures tronquées, aucun corps de méthode, alors que la requête
demande *comment* la clé de cache est construite. Le raisonnement de référence justifiait le PASS par une
affirmation inventée sur le contenu du contexte.

**Effets mesurés par simulation avant application :** le retirage échange `b13-004` contre `b13-007` dans
le golden set ; une seule relecture est invalidée, celle de l'item erroné ; 40 des 41 autres restent
valides ; la composition du golden reste 24 PASS / 26 FAIL. Corpus : 200 exemples, 0 erreur,
103 PASS / 97 FAIL, `cas` 79/81/40.

**`b13-007` quitte `train` : l'adaptateur du 2026-09-20 est périmé.** Le réentraînement est **reporté à la
fin de la relecture**, dix items restant à relire et deux relances ayant déjà été provoquées par des
découvertes. Les règles de sélection du point de contrôle restent celles de l'addendum du 2026-09-20.

---

## Amendement daté — 2026-09-20, audit élargi des items RAG

Onzième et douzième étiquettes corrigées depuis le gel, **avant toute exécution du benchmark**. Simulation
d'impact réalisée sur copie avant application.

Deux règles, dégagées d'un audit de l'ensemble des items `RAG_CONTEXT_RELEVANCE` et appliquées
uniformément :

1. **Aucun symbole visé présent au contexte ⇒ `contexte_pertinent` et `bruit_maitrise` faux.** Vérifiée
   18/18 dans le sens positif. Une violation corrigée : `b12-005`, désormais F F F.
2. **Question en « comment » et contexte réduit à des signatures ⇒ `contexte_suffisant` faux.** Une
   violation corrigée : `b13-007`, désormais V F V / FAIL, `cas` `parfait` → `defaillant`.

`b12-006` et `b14-004` ont été **retirés du périmètre après lecture de leur source** : leur requête nomme
deux entités et la seconde figure bien au contexte. La détection automatique, limitée au premier
identifiant de la requête, était en cause.

**Effets :** le tirage échange `b13-007` contre `b13-004`, une relecture est perdue — celle de l'item
corrigé —, aucune relecture supplémentaire n'est requise. Corpus : 200 exemples, 0 erreur,
102 PASS / 98 FAIL, `cas` 78/82/40, golden 23 PASS / 27 FAIL.

**L'adaptateur reste périmé** et le réentraînement demeure reporté à la fin de la relecture, huit items
restant à présenter.

---

## Amendement daté — 2026-09-21, définition du κ inter-annotateur, avant tout calcul

La §9.1 annonce la publication du κ issu de `data/REVUE_GOLDEN.md` sans dire **contre quelle version de
l'étiquette** il se mesure. La relecture ayant corrigé six étiquettes, dont deux verdicts, la question
n'est pas théorique : elle déplace le chiffre. Elle est tranchée ici **avant d'avoir exécuté
`scripts/kappa_revue.py`**, conformément à la discipline du présent document.

**Définition retenue — l'étiquette telle qu'elle a été présentée.** Le κ mesure l'accord entre le premier
passage en aveugle de l'annotateur et l'étiquette qui lui a été opposée **à ce moment-là**. Les lignes
`étiquette d'origine` et `étiquette (corrigée le matin même)` du journal relèvent donc de cette définition :
dans les deux cas, c'est ce que l'annotateur avait sous les yeux.

**Ce qui est exclu, et pourquoi.**

1. Les lignes `annotateur, après révélation` — un second passage, fait une fois l'étiquette connue. Les
   compter mêlerait un accord obtenu par ancrage à un accord obtenu en aveugle.
2. Les corrections d'étiquette **issues de la relecture**. Les intégrer reviendrait à créditer l'étiquette
   d'un changement que l'annotateur a lui-même provoqué : l'accord mesuré incorporerait le produit de la
   mesure. Le cas concret est `b13-004`, dont l'étiquette présentée disait PASS et l'annotateur FAIL.

**Conséquence assumée sur le chiffre.** Les décomptes courants tenus dans le journal au fil de la
relecture appliquaient la convention inverse — « `b13-004` devient un accord après correction ». Le
chiffre de référence est donc **inférieur d'une unité** à celui que le journal annonçait en cours de route.
Les deux seront publiés côte à côte, le second explicitement désigné comme surestimation.

**Limite à publier avec le κ.** Deux des 50 items — `b04-015` et `b12-005` — n'avaient aucune table dans le
journal ; ils ont été reconstitués depuis une source primaire nommée (tableau récapitulatif de session 1,
transcript horodaté) et consignés en entrées 52 et 53. Pour `b04-015`, seul le contrôle en écart est
attesté : ses trois autres contrôles ne comptent pas dans le κ par contrôle, qui porte donc sur moins
d'observations que le κ du verdict.

**Ce qui n'est pas amendé.** La métrique principale de l'étude reste celle de la §3. Le κ est une mesure de
qualité du corpus de référence, publiée au titre des limites — il ne sert pas à départager les variantes.

---

## Amendement daté — 2026-09-21, défaut de reproductibilité du tirage, corrigé avant l'entraînement final

Relevé en vérifiant, avant de lancer le run unique, que le corpus gelé se régénère bien à l'identique. Il
ne se régénérait pas à l'identique.

**Le défaut.** `scripts/dataset_tools.py` construisait `data/mlx/valid.jsonl`, `data/mlx/test.jsonl` et
`data/golden/test.jsonl` en itérant un `set` de noms de familles. L'ordre d'itération d'un ensemble de
chaînes varie d'un processus à l'autre (randomisation du hachage), si bien que **l'ordre des lignes de ces
trois fichiers changeait à chaque exécution**. `train.jsonl` était épargné parce qu'il itère un `dict`, qui
conserve son ordre d'insertion — c'est ce contraste qui a permis d'isoler la cause.

Le `rng.shuffle(part)` appliqué ensuite est pourtant graîné (`SPLIT_SEED=11`). Il ne corrige rien :
mélanger avec une graine fixe une liste dont l'ordre d'entrée est instable produit une sortie instable. La
graine protégeait d'un aléa, pas de celui-là.

**Ce qui n'était PAS affecté, et qui est prouvé, pas supposé.** L'appartenance et les étiquettes ont
toujours été déterministes : comparaison du golden avant et après régénération — mêmes 50 identifiants,
**0 ligne différente**, seul l'ordre changeant. Le gel du corpus tient donc, et le κ publié plus haut a été
recalculé sur le golden réordonné : chiffres identiques au bit près, recoupements au vert.

**Ce qui était affecté.** L'ordre des lignes détermine l'ordre des lots d'entraînement. À graine égale,
deux exécutions produisaient donc des adaptateurs différents. La §9.3 affirme qu'« un adaptateur LoRA est
figé et rejouable » : cette affirmation était fausse pour la chaîne de données, et elle l'aurait été dans
le REX si le contrôle n'avait pas été fait.

**Le correctif.** `sorted()` sur les deux ensembles de familles avant construction des listes.
**Vérification :** trois exécutions dans trois processus distincts, quatre fichiers chacun, empreintes
SHA-256 identiques. Un premier contrôle avait affiché un faux succès — `shasum` recevant une variable non
découpée par zsh comparait des fichiers vides — et a été refait avec des noms littéraux.

**Conséquence sur les mesures déjà prises.** Le run d'entraînement du 2026-09-20 a utilisé un ordre non
reproductible. Il était déjà périmé pour une autre raison — l'échange `b13-004` / `b13-007` postérieur —
et est archivé sous `adapters/perimes/14b-judge-20260920-2132-avant-echange-b13-004/` et
`mesures/cout/run-20260920-2132-avant-echange-b13-004/`. Ses chiffres de coût restent valables comme ordre
de grandeur, les hyperparamètres étant inchangés, mais l'adaptateur lui-même n'est pas rejouable.

**Ce qui n'est pas amendé.** Ni la métrique principale, ni la composition du corpus, ni les paires de
comparaison déclarées.

---

## Amendement daté — 2026-09-21, le harnais de benchmark ne mettait pas en œuvre le protocole déclaré

Relevé en confrontant `scripts/benchmark_judges.py` au présent document, **avant toute exécution du
benchmark** et pendant l'entraînement du 14B. Aucun résultat n'existe à cette date : aucune des décisions
ci-dessous ne peut avoir été influencée par un chiffre.

Cet amendement **ne modifie aucune quantité déclarée**. Les §4, §5 et §7 restent mot pour mot ce qu'elles
étaient. Il constate que le code en divergeait, et fixe la manière de l'y ramener.

### A. Le κ perd tout pouvoir de décision, et est déclaré secondaire descriptif

Le harnais choisissait la variante gagnante par `max(qualified, key=kappa_mean)`, calculait ses écarts
appariés sur le κ et portait un seuil de gain `--min-kappa-gain` en κ. Or la §4 déclare **une** métrique
principale, la justesse stricte du verdict, et la §6 ne cite pas même le κ parmi les six secondaires.

**Décision.** Le κ est ajouté aux métriques secondaires de la §6, comme **mesure descriptive**. Il continue
d'être rapporté — il est directement comparable au κ inter-annotateur de la relecture du golden, ce qui est
informatif — mais il ne qualifie, ne classe et ne tranche rien. Toute décision se prend sur la justesse
stricte.

### B. La paire de comparaison est déclarée, jamais inférée

Le harnais retenait le comparant par `next((m for m in metrics if m["size"] == size and not
m["fine_tuned"]), None)`. Avec deux variantes 14B non fine-tunées — `14B-baseline-nu` et
`14B-baseline-conventions` — ce `next` choisit **selon l'ordre du JSON**. Il pouvait donc opposer le
fine-tune à `14B-baseline-nu`, soit exactement l'homme de paille que la §3 interdit, et le biais allait
dans le sens favorable au fine-tuning.

**Décision.** Les paires de comparaison sont déclarées explicitement dans `configs/variants.json`, et la
paire principale y est nommée. Si une paire déclarée est absente des métriques, le rapport **échoue
bruyamment** ; il ne retombe jamais sur une inférence.

### C. McNemar exact est implémenté

Déclaré en §5, absent du code. Binomial bilatéral exact sur les seules paires discordantes, α = 0,05,
appliqué à la comparaison principale. Le nombre de paires discordantes est publié avec le p : à n = 50, il
est le vrai déterminant de la puissance.

### D. Le bootstrap passe à 10 000 rééchantillonnages

La §5 déclare 10 000, la valeur par défaut du code était 2 000. Le défaut du code est aligné sur le
document. Le bootstrap apparié porte désormais sur la **différence de justesse**, non sur celle du κ.

### E. L'appareil de qualification n'est pas une règle de conclusion

Le harnais portait des seuils — `min_kappa 0,60`, `min_stability 0,95`, `min_format 0,95`,
`max_verbose_fpr 0,20` — puis élisait un « gagnant » et statuait que « le 32B est justifié ». **La §7 ne
déclare rien de tout cela.** Sa règle de conclusion porte sur la seule comparaison principale et sur la
seule justesse.

**Décision.** Ces seuils sont conservés comme **filtre descriptif de recevabilité opérationnelle** — une
variante qui ne rend pas du JSON exploitable n'est pas utilisable en production, indépendamment de sa
justesse — et le rapport les présente comme tels. Le seuil en κ est supprimé, le κ n'ayant plus de pouvoir.
La conclusion de l'étude est la table de la §7 appliquée à la paire principale, et rien d'autre. La
comparaison 14B / 32B est rapportée de façon descriptive (écart de justesse, coût, latence) sans verdict.

### Ce que cela dit du dispositif

Quatrième instrument du projet trouvé faux avant d'avoir produit un chiffre, après le détecteur de fuites
de surface, le déterminisme du tirage et le parseur du κ. Ce qui l'a attrapé n'est ni un test ni une
relecture, mais la confrontation du code à un protocole écrit **avant** lui. À verser au REX.

---

## Rectification datée — 2026-09-21, sur l'amendement du même jour

L'amendement « le harnais de benchmark ne mettait pas en œuvre le protocole déclaré » affirme, au point E,
que l'appareil de qualification — seuil en κ, élection d'un « gagnant », justification du 32B — était **un
appareil décisionnel entier inventé par le code**.

**C'est faux, et la vérification le montre sans ambiguïté.** `PROTOCOLE.md` §5, sous-section « Décision »,
déclarait mot pour mot : « Qualification — κ ≥ 0,60 ; stabilité du verdict ≥ 95 % ; format strict ≥ 95 % ;
faux PASS sur verbeux ≤ 20 % », « Gagnant — le κ maximal parmi les variantes qualifiées », « Arbitrage
ressources — le 32B n'est retenu que si la borne basse de l'IC95 du Δκ apparié est > 0 et Δκ ≥ 0,05 ».

Le code transcrivait fidèlement ce texte. Il n'avait rien inventé : **il suivait le mauvais document.**

**Le diagnostic correct.** `PREENREGISTREMENT.md` (2026-09-17) a supplanté `PROTOCOLE.md` §5 sans que
celui-ci soit mis à jour, et le harnais, écrit auparavant, est resté fidèle au plus ancien des deux. Les
cinq divergences relevées le matin sont donc réelles et leur correction tient ; seule leur **imputation**
était fautive. `PROTOCOLE.md` §5 est corrigé ce jour, avec mention explicite de sa supplantation plutôt
que par réécriture silencieuse.

**Ce que l'épisode ajoute au REX.** Le risque n'était pas un code négligent mais **deux documents
normatifs divergents**, dont le plus ancien restait exécutable. Un pré-enregistrement ne protège que s'il
supplante explicitement ce qu'il remplace — sans quoi il coexiste avec lui, et c'est le code qui arbitre,
en silence.

---

## Correction datée — 2026-09-21, l'ensemble d'exclusion de la passe « format normalisé » compte 6 items, non 5

L'amendement du 2026-09-19 déclare, au point 2 : « **Exclusion obligatoire** de cette passe : les **5**
items dont la requête impose un format ». Le corpus en porte **six**, et ils portent tous le contrôle
`format_impose` :

```
b04-015  b07-011  b08-013  b09-015  b10-015  b11-010
```

dont **trois figurent au golden set** : `b04-015`, `b07-011`, `b10-015`.

**Aucun n'a été ajouté après l'amendement.** Chacun a reçu `format_impose` dans le commit de création de
son lot, le plus tardif étant `0cdbb7c` (« Add batch 11 and close the code phase at 150 examples »), et
`git log -S'format_impose' -- generators/` ne montre aucun commit postérieur touchant ce contrôle. Les six
existaient donc le 2026-09-19 : **le chiffre déclaré était simplement faux**, et non rendu caduc par une
évolution du corpus.

**Ce qui est corrigé.** L'exclusion porte sur les **6** items portant `format_impose`, définis par ce
contrôle et non par un décompte écrit à la main. La passe « format normalisé » s'exécutera donc sur **47
des 50 items** du golden set, et ce nombre sera publié avec l'écart mesuré.

**Ce qui ne change pas.** Ni la définition de la passe, ni son statut de métrique secondaire, ni la
décision de mesurer et publier la fuite résiduelle plutôt que de la poursuivre.

**Pourquoi cette correction est écrite maintenant.** La passe n'est pas encore implémentée. Fixer
l'ensemble d'exclusion après l'avoir exécutée reviendrait à choisir les items exclus en connaissant leur
effet sur l'écart mesuré. C'est aussi la troisième fois en une journée qu'un nombre écrit à la main est
démenti par la mesure — après les 42 items du parseur de κ et les 39/5/6 de `PROTOCOLE.md` §5. **Règle à
retenir : un ensemble déclaré se définit par un prédicat vérifiable, jamais par un décompte recopié.**

---

## Limite datée — 2026-09-21, l'exclusion de la passe « format normalisé » corrèle avec la difficulté

Relevée en câblant la passe, **avant toute exécution**. Les 3 items du golden set exclus parce que leur
requête impose un format — `b04-015`, `b07-011`, `b10-015` — ne forment pas un sous-ensemble quelconque :

```
tous trois  cas = limite        tous trois  CODE_ANALYSIS        tous trois  verdict = FAIL
```

**Effet sur la composition.** La strate `limite` tombe de 10 à 7 items, soit **30 % de la strate la plus
difficile retirée**, et la part de FAIL de 54 % à 51 %. Le golden dépouillé est donc plus facile et
légèrement plus orienté PASS que le complet.

**Pourquoi ce n'est pas un hasard.** Un item dont la requête impose un format est presque par construction
un cas `limite` : la contrainte de forme y est souvent le seul contrôle qui sépare PASS de FAIL. La
corrélation est structurelle, et elle resterait vraie sur un autre tirage.

**Ce qui reste valide.** L'écart entre les deux passes est **apparié sur des items identiques des deux
côtés** — la justesse de la passe formatée est recalculée sur ces 47 items, jamais sur les 50. L'écart est
donc interprétable comme un effet de forme, et non comme un artefact de l'exclusion. Un contrôle
automatique le vérifie : une variante juste sur les 47 et fausse sur les 3 exclus doit afficher 100 % du
côté formaté ; si elle affichait 94 %, le calcul porterait sur les 50.

**Ce qui est limité.** Le **niveau absolu** des deux passes porte sur un golden amputé, et l'effet de forme
est mesuré sur un sous-ensemble privé précisément des items où la forme compte le plus. L'écart publié est
donc une **borne basse plausible** de la sensibilité au format. Cette réserve est imprimée dans le rapport
lui-même, calculée à l'exécution sur les données présentes plutôt que recopiée.

**Ce qui n'est pas amendé.** Ni l'exclusion, qui reste obligatoire et justifiée — sur ces items la forme
*est* le critère évalué —, ni le statut secondaire de la passe, ni la décision de publier la fuite
résiduelle telle quelle.

---

## Amendement daté — 2026-09-21, la durée publiée excluait les passes de validation

La méthode de substitution déclarée le 2026-09-19, appliquée quand l'horloge est invalidée par une veille
machine, dérive la durée du **débit d'itérations** relevé par mlx-lm : `durée = itérations / débit moyen`.

**Elle ne mesure que les itérations d'entraînement.** Les passes de validation — 9 sur ce run,
14.7 minutes cumulées — en sont absentes. Le chiffre publié valait donc 76.3 min là où
l'utilisateur attend **91.0 min**, soit une sous-estimation de **19%**.

**Correction retenue.** `duree_s` vaut désormais entraînement **plus** validation. Les deux composantes
restent relevées séparément, pour que le partage soit vérifiable.

**Pourquoi c'est légitime après coup.** Le changement rend le coût **moins** favorable à l'étude : 91 min
se défend moins bien que 76. Modifier une définition dans le sens qui dessert son propre argument est
l'inverse d'un choix opportuniste. Il est néanmoins daté et consigné, comme toute autre correction.

**Portée.** Le seuil de détection automatique de veille introduit le même jour dans `train_variant.sh`
compare l'horloge à cette durée **validation incluse**, par cohérence.

---

## Amendement daté — 2026-09-24, un run du banc invalidé : l'adaptateur n'était pas servi

`make bench-14b` a produit le 2026-09-24, de 14h54 à 16h52, les 450 générations des trois variantes 14B.
Le rapport en a tiré la comparaison principale : **« le fine-tuning dégrade la justesse de -76.0 %,
IC95 [-88.0 %, -64.0 %], McNemar exact p = 0.0000 sur 38 paires discordantes »**.

**Cette conclusion est retirée. Elle ne mesurait rien.** `scripts/bench_variant.sh` lançait bien
`mlx_lm.server --adapter-path adapters/14b-judge-ckpt200`, et le serveur a néanmoins répondu avec le
**modèle de base** : aucune erreur, aucun avertissement, 150 réponses plausibles, `BUILD` propre.

**Preuve du diagnostic.** Le même adaptateur, chargé en processus par `mlx_lm.load(adapter_path=...)` et
interrogé sur le même item du golden set avec le même template, rend le format d'entraînement exact —
prose sobre, JSON nu, `{"checks": {...}, "verdict": ..., "reason": ...}` — là où le modèle de base rend
des clés plates dans une clôture markdown, sans `checks` ni `verdict`. Les 150 générations écartées sont
toutes de la seconde forme ; 11 sur 150 seulement contenaient la chaîne `verdict`, contre 150 sur 150
pour `14B-baseline-conventions`. Les trois invites système du golden set sont par ailleurs identiques à
celles de l'entraînement : l'hypothèse d'une dérive d'invite est écartée.

**Ce qui reste valable.** `14B-baseline-nu` et `14B-baseline-conventions` n'utilisent aucun adaptateur :
leurs 300 générations sont intactes, et la comparaison secondaire qui les oppose — **+76.0 points de
justesse pour les conventions seules**, κ passant de 0.00 à 0.48 — tient sans réserve.

**Correction.** L'adaptateur est transmis dans le **corps de la requête** (`"adapters"`), voie déjà
validée côté Java dans `RagContextJudge` sans avoir été reportée ici. Et `sonde_adaptateur()` exige
désormais une **preuve positive** avant de dépenser une heure : un premier appel dont la sortie ne
présente pas le format imbriqué arrête le banc, au lieu de laisser un 0 % être imputé au fine-tuning.

**Portée.** Les générations écartées sont conservées sous `results/runs-invalides/` avec leur notice, et
non supprimées. Le banc de `14B-finetuned` est relancé le 2026-09-24 à 18h47 ; la comparaison principale
reste indécidée jusqu'à son terme.
