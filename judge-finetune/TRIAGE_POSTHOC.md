# Triage par instabilité — analyse a posteriori

**Statut : POST HOC.** Cette analyse n'était pas pré-enregistrée. Elle est née d'une question posée
le 2026-10-14 : *« si le juge ne rend pas le même verdict trois fois, est-ce qu'un humain peut ne
relire que ceux-là ? »* Elle est descriptive et ne qualifie, ne classe et ne tranche rien — même
régime que le κ du juge depuis l'amendement du 2026-09-21.

## La question

Le banc rejoue chaque item du golden set **trois fois**. `verdict_stability` compte les items dont
les trois passes rendent le même verdict (`benchmark_judges.py` ligne 421). On se demande si cette
instabilité est un **signal de confiance** utilisable pour router vers un relecteur humain.

## Méthode

Pour chaque item : verdict de chacune des trois passes, verdict majoritaire, comparaison au verdict
de l'étalon (`data/golden/test.jsonl`, dernier message `assistant`). Croisement stable/instable ×
d'accord/en désaccord avec l'étalon. Script conservé dans le scratchpad de session ; il reproduit
exactement les `verdict_stability` publiées (76 % et 58 %), ce qui vaut contrôle de lecture.

## Résultats

### Variante à conventions — celle que raconte le talk

```
  50 items
  ├─ 38 stables     dont 30 d'accord avec l'étalon,  8 en DÉSACCORD
  └─ 12 instables   dont  8 d'accord avec l'étalon,  4 en désaccord
```

| | |
|---|---|
| Relecture humaine | **12 items sur 50** au lieu de 50 — **−76 % de travail** |
| Désaccords rattrapés | **4 sur 12**, soit **33 %** |
| Désaccords manqués | **8** — rendus trois fois de suite, identiques et faux |

### Variante fine-tunée, pour comparaison

```
  50 items
  ├─ 29 stables     dont 24 d'accord,  5 en DÉSACCORD
  └─ 21 instables   dont 14 d'accord,  7 en désaccord
```

Relecture 21/50 (−58 % de travail), **7 désaccords sur 12 rattrapés (58 %)**.

**Il y a donc un curseur** : plus le juge est instable, plus on relit, plus on rattrape. Ce n'est pas
une propriété du triage, c'est une conséquence mécanique de sa couverture.

## Résultat négatif — router sur un contrôle plutôt que sur le verdict ne sert à rien

Le harnais calcule aussi `decision_stability` : les trois passes doivent rendre **les mêmes
contrôles**, pas seulement le même verdict. On pouvait espérer que router sur « un contrôle a bougé »
attrape plus d'erreurs, puisque 17 items sur 50 portent un désaccord sur au moins un contrôle dont 15
que le verdict masque.

**Ce n'est pas le cas.** Mesuré sur les 47 items dont les trois passes exposent des contrôles
analysables :

| critère de routage | items relus | désaccords rattrapés |
|---|---|---|
| le verdict a bougé | 12 | **4 / 12** |
| un contrôle a bougé | 16 | **4 / 12** |

Un tiers de relecture en plus, **zéro désaccord de plus**. Sur la variante fine-tunée : 30 items
relus au lieu de 21, toujours 7/12. Le levier est une perte sèche, il ne faut pas le proposer.

## Pourquoi 8 désaccords échappent au triage

L'auto-cohérence ne mesure que la part **échantillonnée** de l'erreur. Rejouer le même modèle à
température non nulle fait varier la formulation, pas la compréhension : une convention mal lue est
mal lue de la même façon aux trois passes. Ces erreurs-là sont **systématiques**, et aucune
répétition du même modèle ne les exposera — c'est structurel, pas un défaut de réglage.

## Pour en attraper davantage — pistes, non mesurées ici

1. **Un contrôle déterministe, sans LLM.** `hintCoverage` existe déjà dans le harnais et ne partage
   aucune erreur systématique avec le juge : un item jugé PASS alors que les identifiants attendus
   sont absents du contexte est un signalement qu'aucun rejeu ne produirait. ⚠️ Ne pas dire qu'il
   valide le juge : il corrobore un classement.
2. **Un jury plutôt qu'un juge.** Faire juger par des modèles de **familles disjointes** et router
   sur leur désaccord. C'est le seul levier qui attaque la part systématique, parce que deux familles
   n'ont pas les mêmes angles morts. Référence : Verga et al., *Replacing Judges with Juries:
   Evaluating LLM Generations with a Panel of Diverse Models*, arXiv:2404.18796 (Cohere, 2024) — un
   panel de petits modèles bat un seul gros juge, avec moins de biais intra-modèle et un coût plus de
   sept fois inférieur. Cohérent avec la parade déjà retenue contre l'auto-préférence : ne pas faire
   juger un modèle par sa propre famille.
3. **Un échantillon humain sur les items stables.** Seul moyen d'estimer les 8 manqués sans second
   modèle, et le seul qui mesure au lieu de supposer.

## Limites

- **A posteriori.** Ni l'hypothèse ni le seuil n'étaient déclarés avant la mesure.
- « Désaccord » signifie **désaccord avec l'étalon**, pas faute objective. L'étalon a ses propres
  limites, documentées dans `data/REVUE_GOLDEN.md` : ses étiquettes sont produites par un modèle et
  relues en aveugle par **un** relecteur, pas deux.
- n = 50 items (47 pour la comparaison des critères de routage, faute de contrôles analysables aux
  trois passes sur 3 items). Les effectifs sont petits ; aucun intervalle de confiance n'a été
  calculé, et aucune de ces proportions ne doit être présentée comme une estimation de population.
