# Pré-enregistrement — le plafond de 6000 caractères

Écrit le 2026-10-20, **avant le premier jugement**. Rien de ce qui suit n'est modifiable
après avoir regardé les résultats.

## Ce qu'on mesure et pourquoi

`RagContextJudge` mélange les extraits (graine `question.hashCode()`), les joint, puis
**coupe le texte à 6000 caractères**. Mesuré le 2026-10-19 : **57/180 contextes tronqués**,
répartis très inégalement — `vector` 10/60, `vector-bm25` **46/60** (médiane 4179 caractères
perdus), `graphrag` 1/60. La couverture non-LLM des symboles attendus passe de 68,6 % (vue
par le juge) à **87,4 %** (réelle) pour `vector-bm25`, contre 76,7 % pour `vector`.

Conséquence : le « non concluant » de la paire principale `vector` vs `vector-bm25` peut
être une **cécité de l'appareil de mesure**, pas une égalité. Ce banc tranche.

## Dispositif

Identique au bras A déjà en banque (`benchmarks/rag-campaign-juge-schema-coder32b.jsonl`)
sur tout sauf **un** facteur :

| | bras A (en banque) | bras PLAFOND (ce banc) |
|---|---|---|
| modèle | `qwen2.5-coder:32b` via Ollama | identique |
| invite, critères, conventions | identiques | identiques |
| ordre des extraits | `java_shuffle(hashCode)` | identique |
| sortie structurée | schéma `{checks, verdict, reason}` | identique |
| température / `num_predict` | 0 / 4096 | identique |
| **troncature** | **6000 caractères** | **aucune** |
| `num_ctx` | non fixé (défaut Ollama 4096) | **20480, explicite** |

`num_ctx` doit changer : sans plafond, le plus long contexte fait 54 965 caractères.
**Valeur fixée sur une mesure, pas sur une estimation** — sonde du 2026-10-20 sur les trois
contextes les plus longs, servis sans plafond : l'invite la plus longue pèse **11 896 jetons**
(`prompt_eval_count` relevé au journal d'Ollama). Avec `num_predict` à 4096, il faut au moins
16 000 jetons de fenêtre ; **20480** laisse la marge sans gonfler le cache KV inutilement
(à 32768 le modèle occupait 28 Go sur 36, et le préremplissage tombait à 68 jetons/s).

La même valeur sert aux quatre passes du jour, pour que le modèle ne soit chargé qu'une fois :
un changement de `num_ctx` force Ollama à le recharger (plus de 4 minutes à chaque fois).

Mesuré aussi avant de lancer : l'invite complète **avec** plafond fait au maximum 8020
caractères, soit bien moins que 4096 jetons — **le bras A n'a donc pas subi de troncature
d'invite silencieuse** sous le défaut d'Ollama. Le contrôle de reproduction ci-dessous le
vérifie pour de bon.

### Contrôle de reproduction (avant de dépenser les 180)

12 contextes **non tronqués** tirés du bras A (4 par bras RAG, les premiers par ordre
alphabétique de question) sont rejugés avec `num_ctx=20480` et plafond 6000.
- **≥ 11/12 verdicts identiques** ⇒ le bras A sert de côté « avec plafond », rien à rejouer.
- **≤ 10/12** ⇒ le dispositif n'est pas déterministe d'une configuration à l'autre : on
  rejoue le côté « avec plafond » en entier sous `num_ctx=20480`, et la comparaison se fait
  entre les deux runs neufs.

## Garde-fous (annulent le banc)

1. **> 9 échecs** sur 180 (JSON invalide, exception, timeout) ⇒ banc annulé, rien n'est lu.
2. **Déterminisme** : parmi les 123 contextes que le plafond ne touchait pas, le verdict
   sans plafond doit être le même qu'avec. **> 6 changements sur 123** ⇒ banc annulé : un
   contexte identique rendrait un verdict différent, et aucune comparaison ne tiendrait.

## Les trois questions, et leur lecture, fixées d'avance

### Q1 — principale : `vector` vs `vector-bm25`, sans plafond
McNemar exact apparié, 60 questions, α = 0,05.
- **p < 0,05** ⇒ la paire est concluante. Le chiffre va à l'écran avec la phrase : le
  plafond de l'appareil masquait l'écart.
- **p ≥ 0,05** ⇒ à l'écran : « indiscernables, plafond ou pas ». C'est une mesure, pas une
  cécité, et elle **remplace** la formulation actuelle.

### Q2 — l'effet du plafond lui-même
McNemar exact apparié « avec plafond » vs « sans plafond », **sur les 57 contextes tronqués
seulement**. Descriptif en plus : combien de verdicts basculent, dans quel sens, par bras.
- Ce résultat est **brut** (notes, pas écran) sauf si Q1 bascule : dans ce cas il devient la
  preuve de la phrase de Q1 et passe à l'écran avec elle.

### Q3 — secondaire : `graphrag` vs `vector-bm25`, sans plafond
McNemar exact apparié. Le plafond ne touchait qu'1 contexte sur 60 côté `graphrag`, donc le
biais jouait **contre** `graphrag` : la conclusion actuelle (−31,7 pts) devrait tenir, voire
se renforcer.
- **Sens conservé** ⇒ la conclusion 4 reste à l'écran, chiffre mis à jour.
- **Sens inversé** ⇒ la conclusion 4 **sort** de la présentation, sans discussion.

## Ce qui ne sera pas fait

Aucune autre comparaison n'est déclarée. Toute régularité repérée après coup est notée comme
post hoc et n'a pas le droit d'aller à l'écran sans un nouveau pré-enregistrement.

---

# Résultat — 2026-10-20, 13 h 35

**Garde-fous passés.** 0 échec sur 180. **0 verdict changé** sur les 123 contextes que le
plafond ne touchait pas : le dispositif est déterministe, et le contrôle de reproduction
avait déjà donné **12/12** — le bras A en banque sert de côté « avec plafond », `num_ctx`
n'a aucun effet sur les verdicts.

## Q1 — principale : `vector` ↔ `vector-bm25`, sans plafond

| | PASS |
|---|---|
| `vector` | 60,0 % |
| `vector-bm25` | **78,3 %** |

Écart **+18,3 pts**. Discordantes : `vector` seul **0**, `vector-bm25` seul **11**.
**p = 0,0010**, McNemar exact apparié sur 60 questions.

**Lecture déclarée appliquée : la paire est CONCLUANTE, le chiffre va à l'écran.** La paire
n'était pas à égalité — le plafond de 6000 caractères de l'appareil de mesure masquait
l'écart. Les 11 paires discordantes vont toutes dans le même sens, aucune dans l'autre.

## Q2 — l'effet du plafond lui-même

Sur les **57 contextes tronqués** : 49,1 % de PASS avec plafond, **86,0 % sans**, soit
**+36,8 pts**. Discordantes : **21 FAIL→PASS, 0 PASS→FAIL**, p < 0,0001.

| bras | tronqués | FAIL→PASS | PASS→FAIL |
|---|---|---|---|
| `vector` | 10 | 3 | 0 |
| `vector-bm25` | **46** | **18** | 0 |
| `graphrag` | 1 | 0 | 0 |

La bascule est **unilatérale** : couper le contexte n'a jamais fait passer un contexte de
FAIL à PASS, seulement l'inverse. Q1 ayant basculé, ce résultat passe à l'écran avec elle.

## Q3 — secondaire : `graphrag` ↔ `vector-bm25`, sans plafond

`vector-bm25` 78,3 % contre `graphrag` **16,7 %**, écart **−61,7 pts**, discordantes 38
contre 1, p < 0,0001. **Sens conservé, et nettement renforcé** (−31,7 pts avec plafond).
La conclusion 4 reste à l'écran, avec le nouveau chiffre.

## Taux de PASS par bras

| bras | avec plafond | sans plafond | écart |
|---|---|---|---|
| `vector` | 55,0 % | 60,0 % | +5,0 |
| `vector-bm25` | 48,3 % | **78,3 %** | **+30,0** |
| `graphrag` | 16,7 % | 16,7 % | 0,0 |

## Ce que ça change pour la présentation

1. **La paire principale n'était pas « non concluante », elle était mal mesurée.**
   `vector-bm25` bat `vector` de 18,3 pts, p = 0,0010.
2. **L'ordre des bras change** : avec plafond, `vector` passait devant `vector-bm25`
   (55,0 % contre 48,3 %) ; sans plafond, `vector-bm25` passe devant (78,3 % contre 60,0 %).
   La décision de mise en production s'en trouve confirmée, mais pour la bonne raison.
3. **Le signal non-LLM le disait déjà** : couverture réelle des symboles attendus 87,4 %
   pour `vector-bm25` contre 76,7 % pour `vector`. Le banc et le signal sans LLM concordent
   une fois le plafond retiré, alors qu'ils se contredisaient avec.
4. **La conclusion sur `graphrag` est renforcée**, pas affaiblie : −61,7 pts.
