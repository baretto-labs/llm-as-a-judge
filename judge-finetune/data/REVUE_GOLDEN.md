# Relecture du golden set — journal

But : les étiquettes du corpus sont produites par un modèle. Sans relecture humaine, le κ du benchmark
mesure l'accord avec ce modèle, pas avec un humain. Ce journal trace chaque exemple relu, pour que le κ
soit calculable à la fin et qu'aucun exemple ne soit oublié entre deux sessions.

Golden set : 50 exemples, tirés en `SPLIT_SEED=11`, listés dans `data/golden/test.jsonl` (non versionné,
reproductible par `make split`).

⚠️ **Le golden set a été retiré le 2026-09-15**, après le regroupement des familles RAG par contexte
d'extraction (chantier 7 de l'audit). Ce regroupement a supprimé la fuite — 0 item RAG sur 12 avec un
contexte déjà vu en entraînement, contre 9 sur 11 auparavant — mais il a changé la structure du tirage,
rendant la graine 3 caduque. Composition actuelle : 38 `CODE_ANALYSIS`, 6 `RAG_CONTEXT_RELEVANCE`,
6 `RAG_FAITHFULNESS`, cas 19/21/10, 24 PASS / 26 FAIL.

Conséquence pour la relecture : `b03-007`, relu en session 1, **est sorti du golden set**. Son arbitrage
reste acquis — il a produit la correction de périmètre de `respect_consignes`, appliquée aux 28 exemples
portant un contrôle dédié — mais il ne comptera pas dans le κ du golden. `b04-015`, `b07-011` et
`b10-015` y figurent toujours.

## Protocole

1. L'exemple est présenté **sans son étiquette** : contexte, requête, sortie à évaluer, critères. Ni
   verdict, ni `<thinking>`, ni motif. Montrer l'étiquette d'abord ancrerait l'annotateur, qui validerait
   les erreurs au lieu de les trouver.
2. L'annotateur tranche **chaque contrôle**. Le verdict en découle : PASS si et seulement si tous les
   contrôles sont vrais.
3. L'étiquette est révélée, les écarts sont arbitrés.
4. Toute correction passe par `generators/gen_batch_NN.py` puis `make regen` — **jamais** par le JSONL.
   Si un `verdict` ou un `cas` change, les strates du tirage bougent : rejouer `make split`.

## Ordre de passage

Du plus sujet à erreur au plus simple, pour que l'effort porte là où il compte.

| Session | Contenu | Pourquoi en premier |
|---|---|---|
| 1 | `b04-015`, `b07-011`, `b09-009`, `b10-015` | cas `limite` à 4 contrôles où **un seul contrôle** sépare PASS de FAIL |
| 2 | `b03-012`, `b05-008`, `b06-013`, `b07-015`, `b12-008`, `b13-013` | les 6 autres `limite` : arbitrages, donc divergence maximale entre annotateurs |
| 3-4 | les 10 items RAG restants | portent la posture monde fermé, cœur du fine-tuning |
| 5+ | les 30 `CODE_ANALYSIS` francs | validation rapide |

Plan révisé après le retirage du 2026-09-15. `b09-009` remplace `b03-007` en session 1, même profil : un
`limite` à quatre contrôles dont un seul est faux, donc à une voix de basculer. Les deux `limite` de
session 2 qui sont des items RAG — `b12-008` et `b13-013` — comptent aussi dans les 12 items RAG, d'où
les 10 restants en sessions 3-4.

## Journal

| # | id | Verdict annotateur | Verdict étiquette | Accord verdict | Écart sur les contrôles | Arbitrage |
|---|---|---|---|---|---|---|
| 1 | `b03-007` | FAIL | FAIL | ✅ | `respect_consignes` : annotateur `false`, étiquette `true` | Description corrigée, étiquette inchangée |
| 2 | `b04-015` | FAIL | FAIL | ✅ | `respect_consignes` : annotateur `false`, étiquette `true` | Description corrigée, étiquette inchangée |

**Accord verdict : 2 / 2.** Dont un seul, `b04-015`, encore dans le golden set après le retirage ;
`b03-007` en est sorti et ne comptera pas dans le κ, sans que son arbitrage soit perdu pour autant.

`b07-011` et `b10-015` ont été présentés à l'annotateur, réponse en attente. Tous deux figurent toujours
dans le golden set et n'ont pas été réécrits par la reprise : leurs verdicts restent donc valables.

## Décisions issues de la relecture

### 2026-09-15 — périmètre de `respect_consignes` (exemples 1 et 2)

L'annotateur marquait `respect_consignes` **et** le contrôle dédié à `false` ; l'étiquette ne marquait que
le contrôle dédié. Vérification sur les 200 exemples : la convention était appliquée **15 fois sur 15**,
donc systématique — mais nulle part écrite, et contredisant la description montrée au juge (« Toutes les
consignes obligatoires de la requête sont respectées »). La lecture de l'annotateur était la lecture
littérale, et elle était juste.

Arbitrage retenu : **corriger la description**, pas les étiquettes. Quand un contrôle dédié est présent,
`respect_consignes` annonce désormais qu'elle exclut ce que ce contrôle couvre. Le contrôle dédié garde
ainsi sa valeur de diagnostic — le benchmark peut dire *quelle* contrainte le juge rate, ce qui
disparaîtrait si les deux contrôles basculaient toujours ensemble.

Mis en œuvre dans `generators/gen_batch_01.py` (`RESPECT_CONSIGNES_PERIMETRE_REDUIT`), appliqué aux 28
exemples portant un contrôle dédié. Aucun `verdict` ni `cas` modifié, donc le tirage est inchangé.
