# Minutage et audit des chiffres — mesuré le 2026-10-17

Document de travail, hors écran. Deux questions auxquelles on peut répondre sans
toi : **combien de temps dure le support**, et **chaque chiffre affiché est-il
vrai**.

Méthode du minutage : mots du **script parlé seul** (le commentaire HTML avant le
séparateur `====`, marqueur `[À REFORMULER]` retiré), à **140 mots/min**, débit de
conférence en français. Hors pauses, transitions et construction du schéma — le
réel est donc **au-dessus** de ce qui suit.

Contrôle de lecture : le découpage retrouve **31 diapositives**, le même nombre
que les `<section id=>` du HTML. Total **4292 mots**.

⚠ **Chiffres recalés le 2026-10-17 au soir**, après l'ajout du script de la
quatrième ligne à la diapositive 21 (+97 mots). Le total précédent, 4207 mots /
30,1 min, portait sur le support d'avant cet ajout.

Précision de méthode, écrite parce qu'un recompte intermédiaire a donné
**4453 mots** et a failli être publié : les jetons de **ponctuation isolée**
(« : », « ? » séparés par des espaces) et le terminateur `-->` ne sont **pas**
comptés — ils ne sont pas prononcés. C'est tout l'écart, environ 5 mots par
diapositive. Le contrôle qui tranche : la même méthode appliquée à la version
commise (`git show HEAD:demo/CONFERENCE-V2.md`) rend **4195 mots = 30,0 min**,
soit les 30,1 déjà publiés, et l'écart avec le total courant vaut **97 mots** —
exactement l'ajout. Les sept autres blocs du tableau ci-dessous sont inchangés au
dixième de minute près : **seul le bloc 19-22 bouge**, ce qui est la seconde
preuve que la méthode est bien celle de la veille.

---

## 1. Le support dure 30,7 min pour une cible de 20

**Il y a 10,7 min à couper.** Et le fait important n'est pas le total, c'est la
**forme** de la distribution.

| bloc | diapos | min | part |
|---|---|---|---|
| 1-5 accroche · le problème, les incidents | 5 | 4,3 | 14,0 % |
| 6-10 construire le juge — **méthode** | 5 | 4,8 | 15,5 % |
| 11-14 les trois biais + le cité — **méthode** | 4 | 2,6 | 8,6 % |
| 15-18 RAG, ses pièges, l'étalon — **méthode** | 4 | 4,7 | 15,4 % |
| 19-22 le banc, κ, stabilité, triage | 4 | 4,7 | 15,4 % |
| 23-26 **le résultat — les preuves** | 4 | 4,5 | 14,7 % |
| 27-29 les ratés, ce qui a rattrapé, conclusion | 3 | 4,0 | 13,2 % |
| 30-31 sources · retours | 2 | 1,0 | 3,2 % |
| **TOTAL** | **31** | **30,7** | 100 % |

### Ce que la mesure dit, et qui n'était pas acquis

**Le support est plat, à une exception près.** La médiane est à **52 s**, et la
seule diapositive qui sorte vraiment du lot est la **21** : **2 min 20**, soit
deux fois et demie la médiane, depuis que la quatrième ligne du tableau y a ajouté
son script. Vient ensuite la 18 à **1 min 47**. Rogner les huit plus longues de
30 % ne rendrait que **~2,6 min sur les 10,7** à trouver.

> **Les 10 minutes ne sont pas dans du gras, elles sont dans le nombre de
> diapositives.** Il faut en **retirer une dizaine**, pas les raccourcir.
> Retirer 10 diapos de méthode (moyenne 0,93 min) amène à **21,3 min**.

**Et la mesure confirme la ligne éditoriale déjà arrêtée** — « un REX, pas un
exposé de méthodes : couper la méthode, garder les quatre preuves » :

| | diapos | temps | part |
|---|---|---|---|
| **méthode** (6-18) | 13 | **12,1 min** | **39 %** |
| **preuves** (23-26) | 4 | 4,5 min | 15 % |

Trente-neuf pour cent du temps explique **comment l'instrument est construit**,
quinze pour cent montre **ce qu'il a trouvé**. C'est exactement l'inversion que
la ligne éditoriale annonçait, maintenant chiffrée.

### Les huit diapositives les plus coûteuses

| diapo | min | titre |
|---|---|---|
| **21** | **2,33** | Est-ce qu'il marche, oui ou non ? ⟵ **la plus chère, et de loin** |
| 18 | 1,78 | L'étalon, et la signature que j'y ai trouvée |
| 29 | 1,59 | Trois choses pour vous, une pour moi |
| 2 | 1,36 | Air Canada, 2024 |
| 25 | 1,34 | Moteur, ou traversée de graphe ? |
| 9 | 1,33 | Première question : que ne PAS lui donner à juger |
| 28 | 1,31 | Ce qui a rattrapé chaque instrument |
| 17 | 1,21 | Tout ça, écrit, fait quatre paragraphes |

**Aucune n'est à couper telle quelle** : 18, 21, 25, 28 et 29 portent les
preuves. Le choix des diapositives à retirer est **éditorial, il te revient** —
ce document donne le prix de chacune, pas la décision.

---

## 2. Audit des chiffres affichés

Chaque chiffre à l'écran a été recalculé depuis les données brutes. Pour la
justesse du juge, **le parseur du harnais est importé** (`extract_judgment`,
`majority_verdicts`, `strict_accuracy`) : aucune seconde logique d'extraction ne
peut diverger en silence.

### Un chiffre faux, corrigé

**Diapositive 24, ligne « contexte jugé insuffisant » : affichait 40 % / 66 %.**

Mesuré dans `benchmarks/rag-quality-detail.jsonl`, scénario `hybrid|hybrid`,
contrôle `contexte_suffisant` à faux :

```
  lucene  26/60 = 43,3 %        neo4j  40/60 = 66,7 %
```

Affiché désormais **43 % / 67 %**. Le 40 % était faux de 3 points, **dans le sens
qui flatte la conclusion** : il donnait 26 points d'écart au lieu de 24.

Vérifié qu'il ne s'agissait pas d'un autre contrôle mal étiqueté — aucun ne
produit 40 % : `contexte_pertinent` 38,3/45,0 · `bruit_maitrise` 26,7/26,7.

### Exact au chiffre près

| diapo | chiffre affiché | source recalculée |
|---|---|---|
| 11 | 46 % de faux PASS verbeux | `verbose_fail_false_pass_rate` 0,4583 ✓ (n = 8 items) |
| 12 | 12 verdicts sur 60 basculent | 24 bascules dont **12 à hintCoverage identique** ✓ |
| 13 | 27/23 → 17 recalés, 10 passés, 21 validés, 76 % | vote majoritaire, exact ✓ |
| 18 | 47/50 · 17 incises toutes PASS · 30 sur 30 | `REVUE_GOLDEN.md` l.410, l.744-745 ✓ |
| 21 | κ 0,48 · 0,44 · stab. 76 % · 58 % · format 0 %/100 % | `metrics.json` ✓ |
| 21 | **4ᵉ ligne : 90 % · κ 0,80 · stab. 92 % · format 0 %** | recalculé depuis `results/runs/` ✓ (cf. encadré) |
| 24 | 48 % / 24 % · 24 départagent, 19–5 | 28/58 = 48,3 % · 14/59 = 23,7 % · 19–5 ✓ |
| 25 | 22,0 % avec K-hop · Lucene 48,3 % inchangé | 13/59 = 22,0 % · 28/58 des deux côtés ✓ |
| 26 | inter-modules 8–0 · 5 sur 7 · 6 sur 9 | 8–0, 5–2, 6–3 ✓ (totaux 24 et 19 retombent) |

### La quatrième ligne, et le piège de définition qu'elle a révélé

Les quatre chiffres du `32B-baseline-conventions` ont été recalculés **depuis
`results/runs/` et non depuis `metrics.json`**, parce que le banc Mistral était
en train d'écraser ce dernier. Ils retombent exactement : **90,0 %** de justesse
stricte, **κ 0,80**, **92 %** de stabilité du verdict, **0 %** de format strict.

Mais le contrôle a d'abord échoué, et ce qu'il a trouvé doit être écrit ici parce
que quelqu'un le recalculera : **la colonne κ du support, c'est `kappa_mean`, la
moyenne des trois passes — pas `kappa_majority`.** Les deux clefs existent dans
`metrics.json` et elles ne donnent pas le même nombre :

| variante | `kappa_mean` (à l'écran) | `kappa_majority` |
|---|---|---|
| 14B-baseline-conventions | **0,479** → 0,48 | 0,529 |
| 14B-finetuned | **0,439** → 0,44 | 0,532 |
| 32B-baseline-conventions | **0,801** → 0,80 | 0,801 |

Pour le 32B les deux coïncident, et le 0,80 affiché est donc juste **dans les
deux définitions** — coup de chance, pas méthode. Pour le 14B elles divergent de
cinq centièmes. La raison est mécanique et vaut d'être comprise : les deux
mesures ne se séparent que lorsque le juge est **instable**, puisque le vote
majoritaire lisse ce que la moyenne par passe subit. Le 32B est stable à 92 %,
le 14B à 76 %. **Conséquence pratique : ne jamais comparer un κ du support à un
κ recalculé sur le vote majoritaire.** C'est ainsi que naît un écart apparent
qui n'existe pas.

**Et une bonne nouvelle, vérifiée : l'ambiguïté du 76 % ne se reproduit pas sur
la quatrième ligne.** Le dépôt publie pour chaque variante une « Exactitude »
qui est la **moyenne des trois passes**, tandis que l'écran montre la justesse du
**vote majoritaire** — d'où les 73 % / 76 % de la variante à conventions
(encadré a ci-dessous). Pour le 32B les deux valent **90,0 %**, au dixième près.

| variante | moyenne des passes (`report.md`) | vote majoritaire (écran) |
|---|---|---|
| 14B-baseline-conventions | 73,3 % | **76,0 %** (+2,7) |
| 14B-finetuned | 71,3 % | **76,0 %** (+4,7) |
| 32B-baseline-conventions | 90,0 % | **90,0 %** (+0,0) |

Cet écart **est** la valeur du vote par auto-cohérence, et il s'effondre quand le
juge est déjà stable : il n'y a plus rien à départager. Donc sur la quatrième
ligne, le chiffre du dépôt et le chiffre de l'écran sont le même, et la question
hostile « pourquoi deux exactitudes ? » ne porte que sur les trois premières.

### Deux ambiguïtés armées hors écran

**a) Le 76 %, et ce que publie le dépôt.** `results/report.md` affiche **deux**
chiffres pour la même variante : « Exactitude **73 %** » (moyenne des trois
passes : 70, 76, 74) et « Justesse stricte du verdict (vote majoritaire)
**76,0 %** ». Le support prend le second et il est correctement sourcé — la
matrice 17/10/21 affichée *est* le vote majoritaire, et (17+21)/50 = 76 %. Les
deux sont justes, ce sont deux estimateurs. Réponse courte si on la demande :
*« 76 %, c'est le vote majoritaire des trois passes ; la moyenne passe par passe
donne 73 %. »* Note ajoutée en diapositive 13.

**b) Le 12/60 de la diapositive 12 sous-estime le biais.** Les 12 bascules
surviennent parmi les **39** questions à contenu identique, pas 60 — soit 31 % et
non 20 %. La formulation affichée est donc **conservatrice**, et c'est l'argument
à sortir si on la challenge.

**Et le témoin qui va avec, il est net** : rejoué **avec** la graine, le même bras
Lucene donne **0 bascule sur 60** et 60/60 hintCoverage identiques entre les deux
scénarios. C'est ce qui prouve que la graine a tenu.

### Non vérifiable ici

Les faits externes des diapositives 2 à 5 (Air Canada, Mata v. Avianca, audit
NYC, Deloitte, Chevrolet, les 925/1339 lignes) sont **hors du dépôt** : ils
relèvent des sources citées, pas d'un recalcul. Le statut
« documenté / rapporté par la presse » de la diapositive 3 fait déjà ce partage.

---

## 3. Ce que ce document ne décide pas

- **Quelles diapositives retirer.** Mesuré : le prix de chacune. Éditorial : le
  choix. Il te revient.
- **La phrase manquante à « Le résultat »** (le banc RAG a tourné avec le juge
  fine-tuné, et le support ne le dit pas à l'écran). Formulation proposée dans
  les notes de la diapositive 13.
- **Les 23 scripts `[À REFORMULER AVEC TES MOTS]`.** Ce sont tes mots.

---

## Ce qu'on ne peut pas couper sans casser autre chose — mesuré le 2026-10-17

Le minutage donne le **prix** de chaque diapositive. Il ne dit pas lesquelles se
tiennent entre elles. Voilà les liens, trouvés en découpant le support en 31
diapositives et en cherchant les renvois **dans le texte prononcé seulement**
(avant la ligne `=====`, donc hors notes ⚠).

Contrôle de lecture : le découpage retrouve les **31 `<section>`** du HTML, et les
**9 marqueurs** `[AJOUT AU SCHÉMA]` tombent sur les diapositives **9, 10, 11, 12,
13, 16, 17, 20, 21** — exactement le recalage de `SCHEMA-ETATS.md`, retrouvé par
un autre chemin.

| le lien | qui en dépend | ce qui casse si la source est coupée |
|---|---|---|
| « ne pas faire juger un modèle par sa propre famille, **mon juge est tout seul** — j'y reviens à la fin » | **diapo 14 → 28 et 29** | la promesse est annoncée diapo 14 et réglée **deux fois** |
| « vous vous souvenez, je vous ai dit que **mon juge reçoit le contexte** en plus de la réponse » | **diapos 7 et 15 → 16** | deux ancrages ; le renvoi ne pend que si **les deux** partent |
| « exactement ce que je vous disais tout à l'heure : **un juge qui change d'avis n'est pas un juge** » | **diapo 20 → 22** | le triage de la 22 perd sa raison d'être |
| les 9 marqueurs `[AJOUT AU SCHÉMA]` | **9 → 10 → 11 → 12 → 13 → 16 → 17 → 20 → 21** | chaîne **cumulative** : couper une diapositive porteuse retire un état du dessin |

### Une coupe gratuite, trouvée en cherchant les liens

La dette ouverte diapo 14 est payée **deux fois**, et avec **le même chiffre** :

- **diapo 28** — « Et je vous dois une réponse. Tout à l'heure je vous ai dit de ne
  pas faire juger un modèle par sa propre famille, alors que mon juge, lui, est
  tout seul. Voilà où ça m'a mené : … **et c'est huit fois sur douze**. »
  **70 mots = 30 s.**
- **diapo 29** — « Je vous dois une réponse, parce que je vous ai dit de ne pas
  faire juger un modèle par sa propre famille, et mon juge est tout seul. […]
  Parce que **huit de ses douze erreurs** sont systématiques. »
  **98 mots = 42 s.**

Ce n'est pas deux angles sur la même idée : c'est la même dette, la même
prémisse et le même 8/12, à deux diapositives d'écart. En garder un seul rend
**30 à 42 s** — soit 5 à 7 % des 10 minutes à trouver, sans rien perdre à l'écran
et sans toucher à une seule mesure.

**Lequel garder est éditorial, donc à toi.** Ce qui est mesuré : la 29 est la
plus chère des deux, et c'est elle qui enchaîne sur le jury ; la 28 est celle qui
porte la phrase à retenir.
