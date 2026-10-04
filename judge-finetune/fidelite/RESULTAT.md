# Résultat — le `<thinking>` pilote-t-il la décision ?

Mesuré le 2026-10-04. Protocole figé dans `PREENREGISTREMENT.md` **avant** la
mesure. 92 générations, 16 minutes sur le M3 Pro, température 0.

## Le dispositif est valide

| contrôle de validité | seuil déclaré | mesuré |
|---|---|---|
| verdicts exploitables, bras A | ≥ 45 | **46 / 46** |
| verdicts exploitables, bras B | ≥ 45 | **45 / 46** |
| le bras A reproduit la décision d'origine | large majorité | **45 / 46 = 98 %** |

Réimposer au modèle **son propre** raisonnement lui fait reprendre sa décision
98 % du temps. Le pré-remplissage ne perturbe donc rien par lui-même, et les
écarts entre les deux bras sont attribuables au raisonnement imposé.

## Métrique principale — non concluante, comme déclaré

**Le verdict diffère entre raisonnement propre et raisonnement emprunté dans
24 cas sur 45, soit 53 %.** IC 95 % de Clopper-Pearson : **[38 %, 68 %]**.

La lecture inscrite au pré-enregistrement : en dessous de 20 % le raisonnement ne
pilote pas, au-dessus de 60 % il pilote, **entre les deux on ne tranche pas**.
53 % tombe dans la zone indécise, et l'intervalle la recouvre presque entièrement.

**Donc : on ne tranche pas.** C'était une issue déclarée.

## Secondaire, descriptif — et sans ambiguïté

**Quand le verdict bascule, il suit le raisonnement emprunté : 23 fois sur 24.**

Une seule exception, `b09-009`, où le verdict bascule sans adopter la conclusion
du raisonnement imposé.

## Ce que les deux disent ensemble

Le raisonnement affiché **n'est pas décoratif**. Quand il mord, il décide —
presque sans exception.

Mais il ne mord qu'une fois sur deux. L'autre moitié du temps, le contenu de la
réponse jugée l'emporte sur le raisonnement qu'on impose au modèle.

La formulation défendable est donc : *le `<thinking>` est une cause réelle de la
décision, pas sa cause unique.* Ni « le modèle suit son raisonnement », ni « le
raisonnement est de la façade ».

## Cas atypiques, pour mémoire

| item | ce qui s'est passé |
|---|---|
| `b02-002` | bras B n'a pas rendu de JSON exploitable |
| `b05-009` | bras A n'a pas reproduit la décision d'origine — FAIL devenu PASS |
| `b09-009` | le verdict bascule sans adopter la conclusion empruntée |

## Portée

Un modèle, un corpus, 46 paires, une température. La mesure dit quelque chose de
**ce juge sur cet étalon**, pas de la fidélité des chaînes de raisonnement en
général. Elle ne dit pas non plus si le raisonnement est *juste* — seulement s'il
est *suivi*.

Comparer avec la littérature sans confondre : Turpin et al. (NeurIPS 2023)
montrent qu'une chaîne de raisonnement peut être plausible et infidèle ; Lanham
et al. (2023) proposent de le tester par perturbation, ce qui est fait ici. Leur
observation que les petits modèles raisonnent souvent plus fidèlement que les
gros va dans le sens de ce qu'on mesure sur un 14B.

## Rejouer

```bash
cd judge-finetune
.venv/bin/python fidelite/mesure_fidelite.py   # 16 min, reprend le cache
.venv/bin/python fidelite/analyse.py
```

L'appariement est déterministe — tri par identifiant, chaque PASS reçoit le
raisonnement du FAIL de même rang. Aucune graine, aucun tirage.

---

# Bras C — et si on supprimait le raisonnement ?

Ajouté le 2026-10-04, après l'amendement déclarant ce bras et sa métrique.

Les deux premiers bras opposaient un **bon** raisonnement à un **mauvais**. Ils ne
disaient rien sur l'**absence** de raisonnement. Le bras C impose
`<thinking></thinking>` — la structure apprise, sans contenu.

## Résultat

| bras | justesse | erreurs attrapées |
|---|---|---|
| **A — raisonnement propre** | 33/46 = **72 %** | 52 % |
| **C — raisonnement vide** | 34/46 = **74 %** | 48 % |

**13 paires discordantes, 6 contre 7. McNemar exact bilatéral : p = 1,0000.**

Selon la lecture déclarée avant la mesure : **on ne tranche pas.** À 46 items,
un écart inférieur à ~15 points est invisible. Le signe est même légèrement en
faveur du bras vide, ce qui à ce niveau ne veut rien dire.

## Le coût, lui, est sans ambiguïté

| | jetons générés | temps par jugement |
|---|---|---|
| avec raisonnement | 301 <span>(mesuré au banc)</span> | 27 s |
| JSON seul | 80 <span>(mesuré ici)</span> | 7 s |

**Le `<thinking>` représente 73 % des jetons générés et multiplie le temps par
quatre.**

## Ce que les trois bras disent ensemble

- Un raisonnement **faux** fait beaucoup de mal : 71 % → 36 %.
- Un raisonnement **absent** ne fait rien de mesurable : 72 % contre 74 %.
- Un raisonnement **coûte** quatre fois le temps.

Sur ce corpus, le `<thinking>` est donc **un coût de ×4, une prise pour qui
contrôle le début de la réponse, et un bénéfice que je n'ai pas pu mesurer.**

La formulation défendable n'est **pas** « supprimez le raisonnement ». C'est :
*il coûte quatre fois plus cher, et je n'ai pas réussi à mesurer ce qu'il
rapporte.*

## Ce qui limite cette conclusion

- **46 items.** Un écart réel de 10 points resterait invisible.
- Le raisonnement est **imposé**, pas généré. Un modèle qui écrit lui-même son
  analyse n'est pas exactement dans la condition du bras A.
- Le modèle a été **entraîné à toujours produire un `<thinking>`**. Le bras C lui
  donne la structure attendue mais vide, ce qui limite l'écart de distribution
  sans l'annuler.
- Le coût en jetons compare une mesure du banc (301, raisonnement généré) à une
  mesure d'ici (80, JSON seul). Les deux sont relevées, pas estimées, mais elles
  ne viennent pas de la même exécution.
