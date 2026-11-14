# Pré-enregistrement — seconde relecture du golden set

Écrit le **2026-10-14**, **avant que le second relecteur ait vu un seul item**.

## La question

Le support de conférence affirmait que les 50 items de l'étalon avaient été
« relus en aveugle par deux personnes » et que κ = 0,880 était un accord
**entre humains**. C'est faux, et la correction a été appliquée au support le
2026-10-13.

Ce qui existe aujourd'hui, mesuré le 2026-09-21 et tracé dans
`data/REVUE_GOLDEN.md` :

```
  κ(relecteur 1, étiquette telle que présentée) = 0,880   IC95% [0,720 ; 1,000]
  accord brut 47/50     marges : relecteur 23 PASS / 27 FAIL
                                 étiquette 24 PASS / 26 FAIL
  désaccords : b07-011, b12-007, b13-004
```

Or `data/REVUE_GOLDEN.md` précise en en-tête que **les étiquettes du corpus sont
produites par un modèle**. Ce κ mesure donc l'accord d'un humain avec un modèle,
pas l'accord de deux humains. Il ne peut pas servir de plafond.

**La question posée ici : deux humains appliquant la même grille sur les mêmes
50 items sont-ils d'accord ?** C'est ce chiffre, et lui seul, qui fixe le
plafond du banc : aucun juge automatique ne peut raisonnablement dépasser
l'accord que deux personnes obtiennent entre elles sur la même règle.

## Le dispositif

Le **relecteur 2** est un collègue de l'auteur, extérieur au projet. Il n'a
participé ni à l'écriture du corpus, ni à la première relecture, ni à la
définition des critères.

Protocole **identique à celui de la première relecture** (`REVUE_GOLDEN.md` §
Protocole), reproduit sans modification :

1. Chaque exemple est présenté **sans son étiquette** : contexte, requête, sortie
   à évaluer, **et les critères**. Ni verdict, ni `<thinking>`, ni motif.
   Les critères sont montrés parce que ce qu'on mesure est la reproductibilité de
   la règle, pas l'intuition de deux personnes.
2. Le relecteur tranche **chaque contrôle**. Le verdict en découle : PASS si et
   seulement si tous les contrôles sont vrais.
3. Rien n'est révélé, rien n'est arbitré, **tant que les 50 items ne sont pas
   passés**.

**Ordre de passage** : le même que celui du relecteur 1, des cas `limite` vers
les cas francs. Choisi pour la comparabilité des deux passages. Limite acceptée
et déclarée : les deux relecteurs partagent donc le même éventuel effet d'ordre
et le même profil de fatigue.

**Aucune communication entre les deux relecteurs** sur le contenu des items avant
la fin du passage. Une seule discussion est permise avant le début : les
consignes de protocole ci-dessus.

## Métrique principale, déclarée avant

**κ de Cohen entre le verdict du relecteur 1 (premier passage en aveugle, tel
qu'enregistré dans le journal) et le verdict du relecteur 2**, sur les 50 items,
avec intervalle de confiance bootstrap à 95 %.

Outillage, dit exactement : `scripts/kappa_revue.py` **extrait déjà** le premier
passage en aveugle depuis `REVUE_GOLDEN.md`, et cette extraction est protégée par
ses propres recoupements — une version antérieure rendait 42 items sur 50 en
silence, ce sont les recoupements qui l'ont attrapée. En revanche il compare
aujourd'hui **un relecteur à l'étiquette**, pas deux relecteurs entre eux : il
faudra l'étendre. L'extension ne touchera pas l'extraction. Aucun autre script ne
produira le chiffre publié.

Lecture **fixée à l'avance** :

| κ(R1, R2) | conclusion |
|---|---|
| **≥ 0,80** | la règle est reproductible entre humains. Le plafond est haut, et l'écart avec le κ du juge (0,48) lui est imputable. |
| **0,60 – 0,79** | la règle est reproductible mais imparfaite. Une part de l'écart du juge vient de l'ambiguïté de la grille, pas du modèle. |
| **< 0,60** | la règle **n'est pas reproductible entre humains**. On ne peut pas demander mieux au juge qu'aux auteurs de la règle. Le plafond, c'est la spécification. |

**Si l'intervalle de confiance chevauche deux bandes, la conclusion est « non
concluant »**, et c'est ce mot qui sera employé — pas l'estimation ponctuelle.
À n = 50, c'est une issue probable et elle est acceptée d'avance.

## Mesures secondaires, déclarées sans pouvoir de décision

1. **Accord par contrôle** : sur quel critère les deux humains divergent le plus.
   Descriptif. C'est l'indication la plus directe de ce qu'il faut réécrire dans
   la grille. **Calculable seulement sur le sous-ensemble où les deux relecteurs
   ont marqué chaque contrôle** : au premier passage, `b07-011` a été répondu par
   un verdict seul et `b09-009` n'a pas de colonne verdict. L'effectif exact sera
   donné avec le résultat, jamais arrondi au silence.
2. **Direction du désaccord** : le relecteur 2 est-il plus sévère ou plus
   indulgent que le relecteur 1 ? À comparer à l'asymétrie déjà mesurée au
   premier passage — 16 désaccords sur 22 allaient dans le même sens, l'humain
   plus sévère que l'étiquette écrite par le modèle.
3. **κ(relecteur 2, étiquette)**, reporté **mais jamais publié seul**. Les
   étiquettes ont été corrigées après le premier passage ; `REVUE_GOLDEN.md`
   établit déjà que mesurer contre l'étiquette corrigée surestime l'accord
   (48/50 et κ 0,919 au lieu de 47/50 et 0,880). Ce chiffre n'a donc qu'une
   valeur de comparaison interne.

## Règle d'arrêt

Les **50 items**, sans exception et sans arrêt anticipé. **Le κ ne sera calculé
qu'une fois les 50 passés.** Aucun calcul intermédiaire, aucun coup d'œil au
score en cours de route : le seul moyen de garantir que le résultat n'a pas
orienté la suite de la relecture.

## Conflit d'intérêts, déclaré

Le **relecteur 1 est l'auteur du corpus**. Il juge donc un matériel qu'il a
lui-même produit, ce qui tire mécaniquement l'accord vers le haut. Le relecteur 2
est indépendant, et c'est précisément ce qui donne sa valeur au chiffre. Ce point
sera dit dans l'exposé, sans attendre qu'on le demande.

## Ce qui ne sera pas fait

- **Aucune correction du corpus avant le calcul du κ.** L'arbitrage des écarts
  vient après, et sera tracé comme au premier passage.
- **Aucun ajout ni retrait d'item** pendant la relecture. Toute modification du
  corpus rejouerait `make split` et changerait les 50 items en cours de route.
  Conséquence directe : le chantier de réparation du test de verbosité, s'il a
  lieu, se fera dans un jeu **séparé** (`data/verbosity/`), hors du tirage.
- **Aucune reformulation du κ publié** : si le résultat est inférieur à l'actuel,
  il est publié tel quel. C'est l'objet même de la mesure.

## Ce que le résultat changera dans l'exposé

Quel qu'il soit, il remplace la formulation actuelle des diapositives 19 et 23
(« un relecteur contre mes étiquettes — pas deux humains entre eux ») par le vrai
chiffre inter-humain, et il referme la question hostile n° 1 consignée dans les
notes de la diapositive du QR.

Si la relecture n'est pas terminée à temps, l'exposé garde la formulation
actuelle et annonce : « une seconde relecture est en cours, je publierai le
chiffre. »
