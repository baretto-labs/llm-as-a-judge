# Générateurs et vérifications

Les fichiers JSONL de `data/seed/` ne sont **jamais édités à la main** : les échappements JSON rendent
l'édition manuelle dangereuse, et une frappe accidentée dans un éditeur suffit à corrompre un lot.
Chaque lot est produit par son générateur, de façon déterministe.

## Régénérer

```bash
make regen        # tous les lots, puis validation
```

Ou un seul lot, ce qui est aussi la procédure de réparation :

```bash
.venv/bin/python generators/gen_batch_04.py data/seed/batch_04.jsonl
make validate
```

`gen_batch_01.py` porte la fonction `example()` partagée : elle assemble le message system canonique,
le gabarit du message user, le bloc `<thinking>` et le JSON strict, et déduit le verdict des trois
booléens. Les autres générateurs l'importent.

## Vérifications (`../verification/`)

Chaque affirmation chiffrée d'un `<thinking>` provient de l'exécution d'un de ces fichiers. Ils se
lancent isolément et affichent leurs mesures :

| Fichier | Ce qu'il mesure |
|---|---|
| `FactCheck.java`, `FactCheck02.java`, `FactCheck03.java` | doublons `toMap`, `equals`/`hashCode`, `thenApply`, incréments perdus sur `volatile`, `record` |
| `Probe03.java` … `Probe06.java`, `Probe05b.java` | `Optional.orElse`, dépassement d'entier, `HashMap` partagée, `ThreadLocal` en pool, paresse des flux |
| `factcheck_02.py`, `factcheck_03.py`, `probe04.py`, `probe05.py`, `probe06.py` | injection SQL, arguments par défaut mutables, IBAN, encodage, `__slots__`, comparaison de secrets |
| `probe03_sql.py`, `probe05_sql.py` | `COUNT(*)` sur `LEFT JOIN`, sargabilité, N+1, pagination par `OFFSET` |
| `probe03.ts`, `probe04.ts`, `probe06.ts`, `factcheck03.ts` | `slice`, `forEach` async, liaison de `this`, précision JSON, analyse des dates, clonage |
| `probe03.go` | aliasing de slice, pool de workers |
| `mock_server.py` + `mock_variants.json` | serveur compatible OpenAI simulant 4 juges, pour tester `benchmark_judges.py` sans modèle |

Exemples d'exécution :

```bash
java verification/Probe05.java
python3 verification/probe06.py
go run verification/probe03.go
npx --yes typescript@5 --strict --target es2020 --lib ES2020,DOM \
    --outDir /tmp/ts verification/probe04.ts && node /tmp/ts/probe04.js
```

## Règle de production d'un lot

1. Sonder d'abord le comportement réel, écrire ensuite les exemples à partir des sorties mesurées.
   L'ordre inverse produit des affirmations plausibles mais fausses — cela a été évité plusieurs fois
   (le milieu de recherche binaire ne déborde pas quand `lo = 0`, `sum([0.1]*10) == 1.0` est vrai en
   Python, un micro-banc d'essai ne révèle aucun écart temporel sur `==`).
2. `make validate` doit passer à 0 erreur, puis `make stats` pour contrôler la dérive de distribution.
3. Cocher les familles utilisées dans `data/PLAN_CORPUS.md`.
