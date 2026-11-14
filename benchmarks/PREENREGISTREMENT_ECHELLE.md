# Pré-enregistrement — que fait vraiment une échelle de 0 à 10 ?

**Écrit le 2026-10-19, avant tout jugement.** Fait suite au banc de permutation
(`PREENREGISTREMENT_NOTATION.md`), dont le résultat déclaré est vide : sous permutation, ni la note
ni le verdict ne bougent. Une observation **post hoc** y est apparue — la note n'avait pris que 4
valeurs — sur **12 items seulement**. Elle n'est pas présentable en l'état. Ce banc-ci la met à
l'épreuve sur les 180 contextes de la campagne, avec la question posée **avant** de regarder.

## Questions, dans cet ordre

1. **Dispersion** : combien de valeurs distinctes de l'échelle 0–10 le juge utilise-t-il réellement,
   et comment les 180 notes se répartissent-elles ?
2. **Décision** : la note, binarisée au seuil déclaré, décide-t-elle comme le verdict binaire déjà
   mesuré (`benchmarks/rag-campaign-juge-schema-coder32b.jsonl`) ?
3. **Classement** : la note classe-t-elle les trois bras dans le même ordre que le verdict ?

## Ce que la mesure ne peut pas dire

Les 180 contextes n'ont **aucune étiquette de référence**. On compare deux formats de sortie du
**même juge**, jamais leur justesse. Aucun des deux ne peut être dit « plus juste » ici.

## Dispositif

Identique au juge de contexte de la campagne, **seul le champ final change** : `note` entier 0–10
au lieu de `verdict` PASS/FAIL. Mêmes 3 `checks`, même invite, même modèle
(`qwen2.5-coder:32b` + conventions), température 0, Ollama, schéma imposé, `num_predict` 4096.
Ordre des extraits : celui du moteur, une seule passe par contexte — la permutation a déjà été
mesurée et ne change rien. **180 jugements, ≈ 1 h 40 à 33 s/jugement.**

Seuil de binarisation : **note ≥ 7 ⇒ PASS**, repris tel quel du banc précédent, où il avait été
fixé avant toute mesure.

## Lecture, fixée avant de lancer

**Question 1 — dispersion.** Métrique : nombre de valeurs de l'échelle utilisées au moins 5 fois
sur 180 (≥ 2,8 % des cas), appelées ci-après *valeurs vivantes*.

| valeurs vivantes sur 11 | conduite |
|---|---|
| ≤ 4 | **le chiffre va à l'écran** : l'échelle promet 11 crans et en rend 4 ou moins |
| 5 ou 6 | chiffre brut rapporté, **aucune leçon** à l'écran |
| ≥ 7 | **rien ne va à l'écran** ; l'échelle est bien utilisée et l'observation du 2026-10-19 était un artefact de 12 items |

**Question 2 — décision.** Métrique : nombre de contextes sur 180 où la décision diffère du verdict
binaire déjà mesuré. Rapporté brut, avec son κ. Aucun seuil : c'est une description, et aucune
phrase d'écran n'en dépend.

**Question 3 — classement.** Les trois bras sont ordonnés par note moyenne. Si l'ordre est
identique à celui du verdict (`vector > vector-bm25 > graphrag`), **la concordance va à l'écran** ;
si l'ordre diffère, **on ne montre ni l'un ni l'autre classement comme établi** et on le dit.

**Garde-fou déclaré.** Si plus de 9 jugements sur 180 échouent (schéma illisible, appel en erreur),
le banc est annulé et rien n'en sort — comme pour gemma.

---

## Résultat, 2026-10-19 — lecture appliquée telle qu'écrite

180 jugements, **0 en échec** (garde-fou : 9).

**Q1 — dispersion. Le chiffre va à l'écran.** L'échelle de 0 à 10 n'utilise que **4 valeurs
vivantes** : 1 (×70), 10 (×67), 6 (×28), 0 (×13). Les sept autres crans totalisent **2 jugements
sur 180** : un 2 et un 5. Une échelle à 11 niveaux se comporte donc, en pratique, comme un
classement à quatre crans dont deux concentrent 76 % des cas.

**Q2 — décision.** Accord brut **96,1 %**, **κ = 0,918**, 7 désaccords sur 180. Les deux formats du
même juge décident presque toujours pareil. Description, aucune phrase d'écran n'en dépend.

**Q3 — classement. La concordance va à l'écran.** Par note moyenne : vector 6,68, vector-bm25 5,52,
graphrag 3,05 — **même ordre que par le verdict**.

**Portée, déclarée avec le résultat.** Les 180 contextes sont ceux **coupés à 6000 caractères** par
`RagContextJudge`, troncature répliquée à l'identique et vérifiée (hintCoverage recalculé, 180/180).
Q3 décrit donc la concordance de deux formats du **même juge sur le même texte** ; elle ne dit rien
de la qualité réelle de récupération, mesurée handicapée pour vector-bm25 (46 contextes coupés
sur 60). Voir la mesure du 2026-10-19 sur le plafond.
