# Audit du support — 2026-09-30

49 diapositives. Toutes les remarques du 2026-09-25 sont traitées.

---

## 1. Vérification des chiffres — 43 recalculés, 0 écart

Chaque chiffre affiché à l'écran a été **recalculé depuis les fichiers de
données**, pas relu :

| source | ce qui a été vérifié |
|---|---|
| `benchmarks/rag-quality.jsonl` | 48,3 % · 23,7 % · 39,7 % · 66,1 % · 0,697 · 0,596 · 24 questions · 19–5 · p = 0,0066 · 1,7 point · 8–0 · 5–2 · 6–3 · **témoin Lucene invariant sur les 3 niveaux** |
| `judge-finetune/results/metrics.json` | κ 0,48 et 0,44 · les deux IC · 0 % / 100 % exploitable · format 0 % / 100 % · stabilité 76 % / 58 % · 46 % · les 4 accords par critère |
| `results/runs/*.jsonl` + `data/golden/test.jsonl` | justesse 76 % au vote majoritaire · 16 erreurs recalées sur 27 · 22 bonnes sur 23 · 11 laissées passer |
| recalcul direct | 19–5 → p = 0,0066 · 8–0 → p = 0,0078 · 6–6 → p = 1,0000 · l'exemple de κ : hasard 68, 22 conquis sur 32, κ = 0,69 |
| `OllamAssist/src/main/java` | 162 fichiers Java |

**Aucun écart.** Le script d'audit est reproductible depuis la racine du dépôt.

### Chiffres non recalculables, mais consignés

Ils viennent de mesures antérieures dont l'artefact brut n'est plus dans le
dépôt. Ils sont **documentés**, ce qui reste défendable, mais pas rejouables :

| chiffre | consigné dans |
|---|---|
| κ du corpus 0,880 | `PROTOCOLE.md`, `REX_TRAME.md` |
| κ de `respect_consignes` 0,386 | `REX_TRAME.md` |
| 91 min · 11,32 Go · 43,8 Mo · 169 513 jetons | `REX_TRAME.md` |
| 12 verdicts sur 60 (biais de position) | `REX_TRAME.md` |
| la fuite 17/17 puis 30/30 | `PREENREGISTREMENT.md`, `AUDIT.md` |

---

## 2. Une définition à ne pas confondre en public

**« 76 % de réponses justes » est la justesse au vote majoritaire**, la métrique
principale déclarée avant les résultats. La moyenne des trois passes, elle, vaut
**73,3 %** pour la baseline et **71,3 %** pour le fine-tuné.

Les deux sont dans `metrics.json`. Si quelqu'un lit le dépôt et cite 73,3 %,
ce n'est pas une erreur : c'est une autre définition. La connaître d'avance.

---

## 3. Sources externes

| affirmation | état |
|---|---|
| Air Canada — citation, 650,88 $, membre, 14 février 2024 | **vérifié** sur la décision |
| Air Canada — délai de 90 jours, total avec frais | **non vérifié** — volontairement absents de l'écran |
| Mata v. Avianca — 6 décisions inventées, 5 000 $, juge, date | **vérifié** sur le texte de l'opinion |
| Deloitte Australie — 440 000 AUD, ~97 000 AUD remboursés | **presse concordante** (AP, Fortune, CFO Dive) ; source primaire DEWR **jamais ouverte** |
| NYC MyCity, Chevrolet | **presse seule**, étiquetés comme tels à l'écran |
| CheckEval, EMNLP 2025 — +0,45 sur 12 modèles | **vérifié** sur l'abstract |
| Zheng et al., NeurIPS 2023 | **vérifié** |

**Une seule action avant l'oral :** ouvrir la page DEWR. Si elle ne confirme pas,
basculer la ligne Deloitte dans la catégorie « rapporté par la presse ».

---

## 4. Forme

- **49 notes orateur, aucune vide.** La documentation du fichier est dans le
  front-matter, donc elle ne fuit pas dans la note de la diapositive 1.
- **Zéro terme statistique à l'écran** : plus de σ, de « paires discordantes »,
  de « McNemar », de « bootstrap », de TPR/TNR ni de « taux de PASS ». Tous
  disponibles en notes.
- **7 tableaux sur 49 diapositives**, et seulement trois familles : les principes
  (biais et parades, niveaux de questions, deux κ), le résultat central, et les
  deux tableaux narratifs du REX.
- **7 diapositives dépassent 7 lignes de prose.** Une l'est exprès (« Et ce n'est
  pas un cas isolé », faite pour être survolée et relue). Les six autres sont à
  8 ou 9 lignes : à tailler après la prochaine répétition chronométrée.
- **L'image de la carte Marketplace est un gabarit.** À écraser la veille :
  `demo/img/ollamassist-marketplace.png`, 768 × 638, même nom, puis relancer le
  rendu. Aucun `iframe` ne subsiste.

---

## 5. Le vrai risque restant : le temps

**49 diapositives pour 20 minutes, soit 24 secondes par diapositive.**
C'est le seul point de l'audit qui reste rouge. Le plan d'origine tenait en
20 minutes pile, sans marge, et le support a doublé depuis.

Trois pistes, par ordre de rendement décroissant :

1. **La Partie 2 peut perdre 2 diapositives** — fusionner « La fuite : 17 sur 17 »
   avec « Le correctif qui aggrave », et « Le chiffre spectaculaire » avec sa
   suite. Le récit survit, la mise en scène y perd un peu.
2. **La Partie 3 peut passer de 9 à 7** — fusionner « Le corpus » avec « Tout en
   local », et « Le contrôle qui ne passe pas par le juge » avec « Le résultat ».
3. **Les trois diapositives sur κ peuvent devenir deux** — garder l'exemple chiffré
   et le piège inversé, abandonner l'amorce « On est d'accord 9 fois sur 10 ».

**Rien de tout ça ne se décide sur le papier.** Ça se décide au chronomètre, sur
une répétition à voix haute.

---

## 6. Ce qui reste déclaré non réalisé

- **Le 32B n'a jamais été entraîné.** Deux lignes gelées dans
  `configs/variants.json`, sans données.
- **La passe « format normalisé » n'a pas été jouée.** Elle dirait quelle part de
  l'écart vient de la mise en forme plutôt que du fond. Coût : du temps machine,
  aucune annotation.
- **Aucun échantillonnage de production.** Le projet est entièrement hors-ligne,
  et le support le dit.

Les trois sont **énoncés dans le support**, pas tus.
