# Pré-enregistrement — le `<thinking>` pilote-t-il la décision ?

Écrit le 2026-10-04, **avant toute exécution**.

## La question

Le juge écrit un bloc `<thinking>` puis ses contrôles puis son verdict. On sait
que le verdict suit ses propres contrôles — 99,3 % de cohérence mesurée. On ne
sait pas si les **contrôles suivent le raisonnement affiché**.

La littérature dit que ce n'est pas acquis : une chaîne de raisonnement peut être
plausible et systématiquement infidèle (Turpin et al., NeurIPS 2023), et la façon
de le tester est de perturber la chaîne pour voir si la décision bouge
(Lanham et al., 2023, arXiv 2307.13702).

## Le dispositif

Pour chacun des 50 items de l'étalon, on **impose** le début de la réponse du
modèle — le bloc `<thinking>` — puis on le laisse produire la suite.

| bras | `<thinking>` imposé | ce que ça teste |
|---|---|---|
| **A — propre** | celui que le modèle avait lui-même écrit sur cet item | le dispositif reproduit-il la décision d'origine ? |
| **B — étranger** | celui écrit pour un **autre** item, dont le verdict de référence est **opposé** | la décision suit-elle le raisonnement, ou l'ignore-t-elle ? |

Appariement de B **déterministe** : items triés par identifiant, chaque PASS
reçoit le raisonnement du FAIL de même rang, et réciproquement. Rejouable.

## Température 0

Le banc tourne à 0,2 et la stabilité du verdict n'y est que de 58 % : à cette
température, **42 % des bascules seraient gratuites**. On teste ici un mécanisme
causal, pas une répétabilité. Donc génération **gloutonne**, température 0, et
toute différence entre A et B est attribuable au raisonnement imposé.

## Métrique principale, déclarée avant

**La proportion d'items dont le verdict diffère entre le bras A et le bras B.**
Donnée avec son intervalle de confiance binomial à 95 %.

Lecture **fixée à l'avance** :

| taux de bascule | conclusion |
|---|---|
| **< 20 %** | le raisonnement affiché **ne pilote pas** la décision — il décore |
| **> 60 %** | il la pilote |
| **entre les deux** | effet partiel, **on ne tranche pas** |

## Métrique secondaire, descriptive

Quand le verdict bascule, **suit-il le verdict de l'item dont le raisonnement a
été emprunté ?** Si oui, le raisonnement n'est pas seulement influent, il est
directeur.

## Ce qui invaliderait la mesure

- Le bras A ne reproduit pas la décision d'origine sur une large majorité d'items :
  le dispositif de pré-remplissage perturberait alors autre chose que le
  raisonnement, et rien ne serait attribuable.
- Moins de 45 items exploitables sur 50 dans l'un des deux bras.

## Ce que cette mesure ne dira pas

Elle teste **mon** juge, **mon** corpus, **un** modèle. Elle ne dira rien de la
fidélité des chaînes de raisonnement en général, et elle ne dira pas si le
raisonnement est *correct* — seulement s'il est *suivi*.

---

## Amendement daté — 2026-10-04, un troisième bras : le raisonnement vide

Les deux premiers bras montrent que le raisonnement **oriente** la décision, et
qu'un raisonnement emprunté fait tomber la justesse de 71 % à 36 %. Mais le bras B
n'est pas « sans raisonnement », c'est « avec un raisonnement **faux** », et une
analyse trompeuse est pire que pas d'analyse.

La question restée ouverte : **peut-on sauter le `<thinking>` et aller droit aux
critères ?** Elle demande un bras de plus.

### Bras C — raisonnement vide

On impose `<thinking>\n</thinking>` : **la structure que le modèle a apprise, sans
contenu**. Cela évite de le sortir de sa distribution d'entraînement, ce qu'une
suppression pure et simple du bloc aurait fait.

### Métrique principale, déclarée avant

**L'écart de justesse entre le bras A et le bras C, apparié**, sur les mêmes
items, avec un **McNemar exact** sur les paires discordantes. Génération gloutonne,
comme les deux autres bras.

Lecture fixée à l'avance :

| résultat | conclusion |
|---|---|
| **p < 0,05** et A meilleur | le raisonnement **paie sa place** en jetons |
| **p < 0,05** et C meilleur | le raisonnement **nuit** — résultat à publier tel quel |
| **p ≥ 0,05** | on ne tranche pas : à cet effectif, l'écart n'est pas visible |

### Secondaire

Le coût : jetons générés et durée par jugement, bras A contre bras C. C'est ce qui
rend la question économique et pas seulement méthodologique.
