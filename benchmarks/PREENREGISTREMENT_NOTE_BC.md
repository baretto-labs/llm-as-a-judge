# Pré-enregistrement — note seule contre verdict binaire (bras B et C)

Écrit le 2026-10-20, **avant le premier jugement**. Remplace la mesure d'échelle du
2026-10-19, dont le résultat est **confondu** : le juge rendait les trois booléens *et* la
note, et la note était prévisible à 92,2 % à partir des booléens. Un juge qui n'émet pas les
booléens ne peut pas subir ce biais — c'est tout l'objet des deux bras ci-dessous.

## Les trois bras

Aucun ne mélange note et booléens.

| bras | critères énoncés dans l'invite | sortie | statut |
|---|---|---|---|
| **A** | oui | `{checks, verdict, reason}` | **en banque**, 180 verdicts, rien à rejouer |
| **B** | **non** | `{note, reason}` | à jouer, 180 jugements |
| **C** | **oui** | `{note, reason}` | à jouer, 180 jugements |

- **B** est l'usage courant — « note ce contexte de 0 à 10 » — et le bras dont sort la leçon.
- **C** ne diffère de B que par la présence des critères dans l'invite. Il isole l'effet de
  l'échelle de celui du cadrage.

Tout le reste est identique à A : même modèle (`qwen2.5-coder:32b` via Ollama), même
campagne, même ordre d'extraits (`java_shuffle(hashCode)`), **même plafond de 6000
caractères** — B et C doivent voir exactement ce que A a vu —, température 0,
`num_predict` 4096, sortie structurée par schéma JSON.

`num_ctx` est **fixé explicitement à 20480**, la même valeur que le banc plafond du même
jour, pour que le modèle ne soit chargé qu'une fois. L'invite la plus longue sous plafond
fait 8020 caractères (~2 000 jetons) : aucune troncature d'invite n'est possible. Le contrôle
de reproduction du banc plafond établit si ce réglage change quoi que ce soit par rapport au
défaut sous lequel A a tourné.

## Garde-fou

**> 9 échecs** sur 180 pour un bras ⇒ ce bras est annulé et n'est pas lu. L'autre survit.

## Les quatre questions, et leur lecture, fixées d'avance

**Binarisation déclarée ici, avant toute lecture : `note ≥ 7` vaut PASS.**

### Q1 — principale : l'échelle à 11 niveaux en a-t-elle 11 ?
« Valeur vivante » = une note apparaissant **au moins 5 fois** sur les 180 jugements du bras.
Compté séparément pour B et pour C.
- **≤ 4 valeurs vivantes** ⇒ le chiffre va à l'écran.
- **5 ou 6** ⇒ brut (notes), pas écran.
- **≥ 7** ⇒ rien ne va à l'écran : l'échelle se tient, la leçon n'existe pas.

### Q2 — la note décide-t-elle comme le binaire ?
κ de Cohen entre `note ≥ 7` et le verdict de A, calculé pour B et pour C, plus le taux
d'accord brut. Descriptif : aucun seuil n'est attaché, on rapporte la valeur.

### Q3 — la note classe-t-elle les trois bras RAG comme le verdict ?
Note moyenne par bras RAG (`vector`, `vector-bm25`, `graphrag`) pour B et C, comparée à
l'ordre rendu par le verdict binaire de A.
- **Même ordre dans les trois cas** ⇒ phrase à l'écran : la note coûte plus cher et décide
  pareil.
- **Ordre différent** ⇒ brut, et la phrase ci-dessus est interdite.

### Q4 — les critères changent-ils quelque chose ?
B contre C : écart de valeurs vivantes, κ(B, C), et écart des notes moyennes. Descriptif.

## Ce qui ne sera pas fait

Aucune autre comparaison n'est déclarée. Aucun autre seuil de binarisation que 7 ne sera
essayé. Toute régularité repérée après coup est post hoc et n'ira pas à l'écran sans un
nouveau pré-enregistrement.

---

# Résultat — 2026-10-20, 13 h 40

**Garde-fou passé** : 0 échec sur 180 pour B, 0 pour C.

## Q1 — principale : l'échelle à 11 niveaux en a-t-elle 11 ?

**Bras B — note seule, sans critères** : `0×128  2×21  5×2  6×1  8×25  10×3`
→ **3 valeurs vivantes** (0, 2, 8). Sur une échelle de 11 niveaux, trois crans portent
174 des 180 jugements, et **128 sur 180 valent zéro**.
**Lecture déclarée appliquée : le chiffre VA À L'ÉCRAN** (seuil : ≤ 4).

**Bras C — note seule, critères énoncés** : `0×44  1×2  2×42  3×2  5×1  6×9  7×12  8×68`
→ **5 valeurs vivantes** (0, 2, 6, 7, 8).
**Lecture déclarée appliquée : brut, pas écran** (seuil : 5–6).

## Q2 — la note décide-t-elle comme le binaire ?

| bras | accord brut avec A | κ | désaccords |
|---|---|---|---|
| **B** (note seule) | 73,3 % | **0,381** | 48/180 |
| **C** (note + critères énoncés) | 92,2 % | **0,841** | 14/180 |

## Q3 — la note classe-t-elle les trois bras comme le verdict ?

Ordre du verdict binaire de A : `vector` (55,0 %) > `vector-bm25` (48,3 %) > `graphrag` (16,7 %).

| bras | notes moyennes | ordre |
|---|---|---|
| **B** | vector 1,27 · vector-bm25 2,33 · graphrag 1,20 | `vector-bm25 > vector > graphrag` — **différent de A** |
| **C** | vector 5,60 · vector-bm25 4,68 · graphrag 2,70 | `vector > vector-bm25 > graphrag` — identique à A |

**Lecture déclarée appliquée : l'ordre diffère pour B, donc brut, et la phrase « la note
coûte plus cher et décide pareil » est interdite à l'écran.**

## Q4 — les critères changent-ils quelque chose ?

B contre C sur les mêmes 180 items : **notes identiques 46,1 %**, **κ(B, C) = 0,278**.
Note moyenne **1,60** contre **4,33**, écart **+2,73 points sur 10**. Une fois binarisées
au seuil déclaré de 7 : accord 71,1 %, κ = 0,374.

## Ce qui va à l'écran, et ce qui n'y va pas

**À l'écran** — un seul chiffre, celui que Q1 autorise : demander une note de 0 à 10 sans
rien dire d'autre donne **3 valeurs utilisées sur 11**, dont **zéro dans 71 % des cas**.
L'échelle fine est une illusion : le juge rend un interrupteur déguisé en potentiomètre.

**Pas à l'écran, mais noté** : énoncer les critères sans les faire sortir déplace la note
moyenne de **+2,73 points** et fait passer l'accord avec le verdict binaire de κ 0,381 à
0,841. Ce n'est pas l'échelle qui porte l'information, c'est le cadrage.

**Observation post hoc, non présentable en l'état** : l'ordre rendu par B
(`vector-bm25 > vector`) est celui que le banc plafond du même jour établit comme correct,
alors que A et C rendent l'ordre inverse — mais A et C ont tous deux tourné **sous le
plafond de 6000 caractères**. Rapprocher les deux demanderait de rejouer B et C sans
plafond, et un nouveau pré-enregistrement.
