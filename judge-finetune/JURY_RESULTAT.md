# Résultat — jury de familles disjointes

Banc `Mistral-24B-baseline-conventions` terminé le **2026-10-17 à 15 h 44**,
150 générations, 50 items × 3 passes. Lecture appliquée telle qu'écrite dans
`PREENREGISTREMENT_JURY.md` le même jour, **avant toute génération**.

## Métrique principale, telle que déclarée

**2 sur 8.** Sur les huit items que le juge rend trois fois identiques et faux,
Mistral n'est en désaccord que sur deux : `b09-014` et `b12-011`.

| | |
|---|---|
| bande atteinte | **≤ 3 sur 8** |
| conclusion déclarée d'avance | le jury ne fait **pas mieux qu'un entraînement de plus** |
| plancher posé d'avance | l'entraînement seul corrigeait **3 sur 8** |

n = 8. Aucun intervalle de confiance, aucune valeur-p, aucun pourcentage — comme
déclaré. **La bande est appliquée sans renégociation : la diapositive 29 doit
changer.**

### Et la direction du désaccord, qui n'était pas demandée mais qui saute aux yeux

**Sept des huit items sont étalon FAIL / juge PASS.** Le juge ne se trompe pas au
hasard sur ses erreurs systématiques : il est **trop indulgent**. Et Mistral
partage cette indulgence sur six d'entre eux. Deux familles sans ancêtre commun,
le même biais de complaisance, sur les mêmes items.

## Mesures secondaires, déclarées sans pouvoir de décision

| | |
|---|---|
| **coût** | **11 items sur 50** à relire — sous le seuil de 25 posé d'avance |
| **triage seul** | 12 relus, **4/12** désaccords couverts |
| **jury seul** | 11 relus, **4/12** couverts |
| **triage ∪ jury** | 18 relus, **6/12** couverts |
| **cibles fine-tunées** | **1 sur 5** en désaccord |
| **justesse stricte de Mistral** | **70,0 %** — aucun pouvoir de verdict |

Le Δ de justesse contre le juge est **−6,0 points, IC95 [−18,0 ; +6,0],
McNemar p = 0,5488** sur 11 paires discordantes, produit par la paire
pré-déclarée. Rien n'est détectable, et cette variante confond famille et taille
(24B contre 14B) : ce chiffre ne dira jamais qu'une famille juge mieux qu'une
autre.

Noter quand même, puisque c'est le seul endroit où le jury gagne quelque chose :
**l'union des deux leviers couvre 6 des 12 désaccords pour 18 relectures**, là où
le triage seul en couvre 4 pour 12. Descriptif, et ce n'est pas la question posée.

---

## POST HOC — ce que les deux bancs disent ensemble, et qui contredit le pré-enregistrement

**Statut : POST HOC, non déclaré d'avance.** À lire avec la même réserve que
`TRIAGE_POSTHOC.md`. La mesure qui suit n'a pas de pouvoir de décision et n'a pas
servi à choisir la bande ci-dessus.

Le pré-enregistrement annonçait, pour la bande ≤ 3/8 : « les erreurs ne sont pas
imputables à la famille : elles sont dans le corpus ou dans la grille », et
ajoutait que « ce résultat converge avec l'hypothèse de plafond que teste le banc
32B ».

**La première moitié tient. La seconde est fausse, et c'est le banc 32B qui l'a
réfutée** en rendant 90 % sur le même corpus avec la même invite. Les deux bancs
avaient donc l'air de se contredire : Mistral dit « ce n'est pas la famille »,
donc on accuse le corpus ; le 32B dit « le corpus va très bien ».

La mesure qui sépare les deux lectures, c'est **ce que le 32B fait sur ces huit
items nommés** :

| item | étalon | juge 14B | **32B** | Mistral | fine-tuné |
|---|---|---|---|---|---|
| `b03-005` | FAIL | PASS | **FAIL ✓** | PASS | FAIL ✓ |
| `b03-014` | FAIL | PASS | **FAIL ✓** | PASS | PASS |
| `b04-002` | FAIL | PASS | PASS | PASS | PASS |
| `b04-014` | FAIL | PASS | **FAIL ✓** | PASS | PASS |
| `b06-008` | FAIL | PASS | PASS | PASS | PASS |
| `b07-002` | FAIL | PASS | PASS | PASS | PASS |
| `b09-014` | PASS | FAIL | **PASS ✓** | PASS ✓ | PASS ✓ |
| `b12-011` | FAIL | PASS | **FAIL ✓** | FAIL ✓ | FAIL ✓ |

**Le classement des trois leviers, sur les mêmes huit items :**

| levier | ce qu'il change | corrige |
|---|---|---|
| **jury** — autre famille, 24B | la famille | **2 sur 8** |
| **entraînement** — même famille, même taille | les poids | **3 sur 8** |
| **taille** — même famille, plus gros | la capacité | **5 sur 8** |

Donc, et c'est la lecture qui réconcilie les deux bancs : **ces erreurs ne sont
ni un angle mort de famille, ni un défaut de corpus. C'est un plancher de
capacité.** Un modèle d'une autre famille les répète ; un modèle de la même
famille, plus gros, en corrige la majorité. Ce que le jury attaquait — des
angles morts disjoints entre familles — **n'existe pas sur ce jeu** : les deux
familles ont le même angle mort, et il est dans la même direction (l'indulgence).

### Les trois items que rien ne corrige

`b04-002`, `b06-008`, `b07-002` sont rendus **PASS par les quatre
configurations** — deux familles, deux tailles, entraîné et non entraîné — alors
que l'étalon dit FAIL. Ce sont les seuls candidats sérieux à un défaut de corpus
ou de grille, et c'est **là** qu'il faut regarder, pas sur les huit.

⚠ **Candidat, pas conclusion** — à l'écriture de ce paragraphe. n = 3, post hoc,
et « l'étalon dit FAIL » ne veut pas dire que l'étalon a raison : ses étiquettes
sont produites par un modèle et relues par **un** relecteur
(`data/REVUE_GOLDEN.md`). Quatre modèles d'accord contre l'étiquette est
exactement le profil d'une étiquette discutable — et exactement celui d'un cas
difficile. Les distinguer demandait de **lire les trois items**.

### Les trois items ont été lus — 2026-10-17, et l'étalon tient

Lecture manuelle des trois `user` / `assistant` dans `data/golden/test.jsonl`
(index 21, 27, 15 ; l'identifiant est dans `meta`, pas à la racine). **Aucun
défaut de corpus.** Dans les trois cas l'affirmation centrale de la copie est
fausse, et le `<thinking>` de l'étalon la réfute par un contre-exemple
vérifiable :

| item | la copie affirme | réfutation portée par l'étalon |
|---|---|---|
| `b04-002` | « `Arrays.asList` renvoie une liste immuable » | c'est une **vue de taille fixe** : `add`/`remove` lèvent, mais `Arrays.asList("a","b").set(0,"z")` **réussit** |
| `b06-008` | « ajouter `T00:00:00` force une lecture cohérente » | mécanisme **inversé** : `"2026-03-01"` est lu en **UTC**, `"2026-03-01T00:00:00"` en **local** — à UTC+1 le second vaut `2026-02-28T23:00:00Z`, le correctif **crée** le décalage |
| `b07-002` | « c'est de la contention, passez en verrou équitable » | c'est un **interblocage par ordre d'acquisition inversé** ; l'équité ordonne les prétendants à un même verrou, elle ne casse pas une dépendance croisée |

**Le motif est commun aux trois, et c'est lui le résultat** : l'erreur centrale
est enrobée de **plusieurs développements annexes exacts et bien écrits** —
l'idiome `toArray(new String[0])`, l'exposition de la représentation interne,
l'indexation à zéro de `getMonth()`, `tryLock`/`lockInterruptibly`/`Condition`,
le `unlock()` dans le `finally`. Les quatre configurations valident une copie
d'expert sans peser la phrase qui compte plus lourd que celles qui l'entourent.

C'est le **biais de verbosité dans sa forme adulte** : la parade appariée de la
diapositive 11 fait varier la *longueur* à défaut égal, pas la *densité de vrai
autour du faux*. Elle ne peut donc pas attraper ces trois-là, et la mesure de
46 % de faux PASS sur défauts bavards ne les couvre pas.

⚠ Ce qui reste limité : n = 3 et post hoc. La lecture ferme la question
« corpus ou modèle ? » — c'est le modèle — mais elle ne mesure pas la fréquence
du motif, et aucun test n'a été construit pour lui. C'est une **piste outillable**
(un jeu apparié *erreur bien entourée* / *erreur nue*), pas un résultat chiffré.

## Ce que cela change dans l'exposé

La bande impose que la diapositive 29 change : le jury ne peut plus y figurer
comme la suite annoncée. **Ce qui le remplace est éditorial et n'est pas tranché
ici** — la mesure dit seulement que la piste désignée par les chiffres n'est plus
« des familles disjointes » mais **la capacité, et trois items à relire**.
