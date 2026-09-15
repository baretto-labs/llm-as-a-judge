# Relecture du golden set — journal

But : les étiquettes du corpus sont produites par un modèle. Sans relecture humaine, le κ du benchmark
mesure l'accord avec ce modèle, pas avec un humain. Ce journal trace chaque exemple relu, pour que le κ
soit calculable à la fin et qu'aucun exemple ne soit oublié entre deux sessions.

Golden set : 50 exemples, tirés en `SPLIT_SEED=3`, listés dans `data/golden/test.jsonl` (non versionné,
reproductible par `make split`).

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
| 1 | `b03-007`, `b04-015`, `b07-011`, `b10-015` | cas `limite` à 4 contrôles où **un seul contrôle** sépare PASS de FAIL |
| 2 | les 6 autres `limite` | arbitrages, donc divergence maximale entre annotateurs |
| 3-4 | les 11 items RAG | portent la posture monde fermé, cœur du fine-tuning |
| 5+ | les 29 PASS/FAIL francs | validation rapide |

## Journal

| # | id | Verdict annotateur | Verdict étiquette | Accord verdict | Écart sur les contrôles | Arbitrage |
|---|---|---|---|---|---|---|
| 1 | `b03-007` | FAIL | FAIL | ✅ | `respect_consignes` : annotateur `false`, étiquette `true` | Description corrigée, étiquette inchangée |
| 2 | `b04-015` | FAIL | FAIL | ✅ | `respect_consignes` : annotateur `false`, étiquette `true` | Description corrigée, étiquette inchangée |

**Accord verdict : 2 / 2.**

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
