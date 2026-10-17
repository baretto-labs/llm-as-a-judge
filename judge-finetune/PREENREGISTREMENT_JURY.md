# Pré-enregistrement — jury de familles disjointes

Écrit le **2026-10-17**, **avant que le modèle Mistral ait vu un seul item**.
Aucune génération n'existe pour la variante `Mistral-24B-baseline-conventions`
au moment où ce document est écrit : `results/runs/` n'en contient pas de fichier.

## La question

La diapositive 29 du support annonce la suite comme **un jury de familles
disjointes**, au motif que les erreurs systématiques du juge échappent à tout
rejeu du même modèle. L'argument vient de `TRIAGE_POSTHOC.md` § « Pourquoi 8
désaccords échappent au triage », et il est **raisonné, pas mesuré** : rien dans
le dépôt ne montre qu'un modèle d'une autre famille tranche autrement sur ces
items. C'est la dernière affirmation non mesurée qui reste à l'écran.

**La question posée ici : un modèle d'une famille disjointe, à conventions
identiques, est-il en désaccord avec le juge sur les items que le juge rend
trois fois identiques et faux ?**

C'est la condition d'existence du levier. Si les deux familles se trompent sur
les mêmes items, l'erreur n'est pas dans le modèle, elle est dans le corpus ou
dans la grille — et le jury ne l'atteindra pas.

### Ce que l'entraînement fait déjà, pour avoir un point de comparaison

Mesuré le 2026-10-17 sur `results/runs/`, en réutilisant l'extraction de verdict
du harnais (`extract_judgment`), et **recoupé** contre les effectifs publiés dans
`TRIAGE_POSTHOC.md` (38/30/8/12/8/4 et 29/24/5/21/14/7, reproduits à l'identique
avant que la moindre cible soit émise) :

Les **8 erreurs systématiques** du juge à conventions, une fois le même modèle
entraîné, deviennent :

| devenir | items |
|---|---|
| **corrigées** — 3 sur 8 | `b03-005` `b09-014` `b12-011` |
| **instables**, donc rattrapables par le triage — 4 sur 8 | `b04-002` `b04-014` `b06-008` `b07-002` |
| **systématiques encore** — 1 sur 8 | `b03-014` |

Donc, à l'intérieur d'une même famille, un simple changement d'entraînement
**déplace déjà 7 des 8 erreurs systématiques**. « Systématique » n'est pas une
propriété de l'item : c'est une propriété du couple modèle + invite. Ce 3/8
corrigé est le **plancher** que le jury doit battre pour valoir mieux qu'un
entraînement de plus — celui-là même que le support renonce à refaire.

## Le dispositif

**`Mistral-24B-baseline-conventions`**, déclaré dans `configs/variants.json` le
2026-10-17 avec sa paire de comparaison, port 8085 :

| | |
|---|---|
| modèle | `mlx-community/Mistral-Small-3.2-24B-Instruct-2506-4bit` |
| famille | Mistral — **aucun ancêtre de pré-entraînement commun avec Qwen** |
| adaptateur | aucun. **Rien n'est entraîné**, c'est une invite à conventions |
| suffixe système | `configs/conventions.md`, **le fichier identique** à celui des variantes Qwen |
| items, passes, température | les **mêmes 50**, **3 passes**, T = 0,2 |
| harnais | `scripts/bench_variant.sh`, inchangé |

**Mistral et non Gemma 3** : Gemma traite le rôle `system` autrement, et les
conventions passent précisément par `system_suffix_file`. Un suffixe non
appliqué en silence rendrait une ligne de résultats d'apparence normale sur un
juge sans conventions — exactement le mode de défaillance que l'exposé prend
pour conclusion. **Mistral et non phi-4** malgré sa taille mieux appariée :
16 k de contexte, alors que les invites de ce banc montent à ~930 jetons de
contexte plus la réponse, et aucune spécialisation code.

## Métrique principale, déclarée avant

**Sur les 8 items systématiquement faux du juge à conventions, nommés
ci-dessus, le nombre sur lequel Mistral rend un verdict différent.**

Les 8 cibles sont **gelées ici** : `b03-005` `b03-014` `b04-002` `b04-014`
`b06-008` `b07-002` `b09-014` `b12-011`. Aucune ne sera ajoutée ni retirée
après lecture des résultats.

Le verdict étant binaire et le juge étant faux sur ces 8, « Mistral est en
désaccord avec le juge » et « Mistral a raison » sont **la même proposition**
sur ce sous-ensemble. C'est ce qui rend la mesure exploitable à si petit
effectif : elle ne demande pas d'estimer une justesse, seulement de compter des
désaccords sur des items dont l'étiquette est connue.

**n = 8. Aucun intervalle de confiance ne sera calculé, aucune valeur-p, et le
chiffre ne sera jamais présenté en pourcentage** — un « 62,5 % » sur 8 items
suggère une précision qui n'existe pas. Il sera écrit « 5 sur 8 », même régime
descriptif que `TRIAGE_POSTHOC.md`.

Lecture **fixée à l'avance** :

| désaccords sur les 8 | conclusion |
|---|---|
| **≥ 6 sur 8** | les erreurs systématiques sont **propres à la famille**. Le levier existe, il va à l'écran avec son coût. |
| **4 ou 5 sur 8** | au-dessus du plancher de l'entraînement (3/8) mais **non concluant** à cet effectif, et c'est le mot qui sera employé. Chiffre brut rapporté, aucune affirmation à l'écran. |
| **≤ 3 sur 8** | le jury ne fait **pas mieux qu'un entraînement de plus**. Les erreurs ne sont pas imputables à la famille : elles sont dans le corpus ou dans la grille. La diapositive 29 doit changer, et ce résultat converge avec l'hypothèse de plafond que teste le banc 32B. |

## Mesures secondaires, déclarées sans pouvoir de décision

1. **Le coût, et il est déclaré avec son seuil.** Nombre d'items sur 50 où
   Mistral et le juge divergent — c'est le volume que le jury envoie au
   relecteur, l'équivalent des « 12 relectures » du triage. **Seuil fixé
   d'avance : au-delà de 25 sur 50, le levier fait relire plus de la moitié du
   jeu et sera rapporté comme trop coûteux quelle que soit sa couverture.**
   Un levier qui attrape tout en relisant tout n'est pas un levier.
2. **Triage ∪ jury** : items signalés par l'un *ou* l'autre critère, couverture
   des 12 désaccords et coût en relectures. Descriptif. C'est la seule forme
   sous laquelle les deux leviers seraient proposés ensemble.
3. **Les 5 erreurs systématiques de la variante fine-tunée** — `b01-005`
   `b02-001` `b03-001` `b03-014` `b10-015` — mesurées de la même façon, et
   déclarées ici parce que **l'arbitrage de variante du support est encore
   ouvert** (cf. `WIP.md`, matrice de la diapositive 14, et la contradiction
   22/29 relevée le 2026-10-17). Déclarer les deux jeux avant toute génération
   est ce qui empêche de choisir le plus flatteur après coup.
4. **Justesse stricte de Mistral sur les 50 items**, rapportée **sans aucun
   pouvoir de verdict**. À n = 50 l'étude ne détecte pas en dessous de ~15
   points (`PREENREGISTREMENT.md` § 5), et cette variante **confond famille et
   taille** : 24B contre 14B. Conforme à la décision déjà prise — « aucune
   règle d'arbitrage entre tailles ». Ce chiffre ne servira jamais à dire
   qu'une famille juge mieux qu'une autre.

## Confusions, déclarées

- **Taille** : 24B contre 14B. Sans effet sur la métrique principale, qui
  compare des **ensembles d'items** et non des niveaux de justesse. Rédhibitoire
  pour toute comparaison de justesse, d'où la mesure 4 sans pouvoir de décision.
- **Spécialisation** : Qwen2.5-Coder est spécialisé code, Mistral Small est
  généraliste. Un désaccord peut donc venir de la famille *ou* de la
  spécialisation. L'expérience ne les sépare pas, et ne prétendra pas le faire.
- **Un seul modèle n'est pas un jury.** Ce banc mesure la **condition
  nécessaire** du levier — l'existence d'angles morts disjoints — pas la
  performance d'un jury. Aucune ligne ne dira « un jury fait mieux ».

## Règle d'arrêt

Les **150 générations**, 50 items × 3 passes, sans arrêt anticipé et sans
examen intermédiaire des verdicts. Le décompte des 8 cibles ne sera fait
**qu'une fois les 150 passées**.

## Ce qui ne sera pas fait

- **Aucune relance avec une autre famille si le résultat déplaît.** Mistral est
  déclaré ici, c'est le modèle dont le résultat sera publié. Essayer Gemma
  ensuite et garder le meilleur serait choisir la famille après les chiffres.
- **Aucune modification des 4 conventions** pour ce modèle. Le fichier est le
  même, à la ligne près ; c'est tout l'intérêt.
- **Aucun ajout d'item**, pour la même raison qu'en relecture 2 : cela rejouerait
  `make split`.
- **Aucune règle d'arbitrage inventée après coup**, cf. `WIP.md`.

## Ce que le résultat changera dans l'exposé

Il tranche la dernière phrase non mesurée du support. Selon la bande atteinte,
la diapositive 29 **garde** le jury comme suite annoncée en citant sa couverture
et son coût, ou **l'abandonne** au profit de ce que le résultat désigne alors :
le corpus et la grille.

**Statut vis-à-vis de l'exposé.** `WIP.md` avait versé le jury multi-modèles à
l'article de blog, au motif qu'il faudrait rattraper 10 des 12 désaccords pour
conclure quoi que ce soit. Cette décision est **réouverte sciemment**, et la
raison est que la question a changé : il ne s'agit plus de conclure qu'un jury
juge mieux — hors de portée à n = 50 — mais de vérifier la **condition
d'existence** du levier sur 8 items nommés. Si la mesure n'est pas faite à
temps, la diapositive 29 ne cite aucun chiffre et dit « c'est la piste, elle
n'est pas encore mesurée ».
