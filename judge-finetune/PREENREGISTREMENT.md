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
