"""Contrôle de reproduction du banc plafond — règle fixée dans
benchmarks/PREENREGISTREMENT_PLAFOND.md : >= 11/12 verdicts identiques au bras A en banque,
sinon le côté « avec plafond » doit être rejoué en entier.

Sort 0 si le bras A peut servir tel quel, 1 s'il faut le rejouer.
"""
import json, sys

BANQUE = "benchmarks/rag-campaign-juge-schema-coder32b.jsonl"
ref = {(d["arm"], d["question"]): d["contextVerdict"]
       for d in map(json.loads, open(BANQUE))}

ok = total = 0
for d in map(json.loads, open(sys.argv[1])):
    if d["sortie"] is None:
        print(f"  ECHEC   {d['arm']:11} {d['question'][:60]}")
        total += 1
        continue
    a, b = ref[(d["arm"], d["question"])], d["sortie"]["verdict"]
    total += 1
    ok += a == b
    print(f"  {'=' if a == b else 'DIFF':4}    {d['arm']:11} banque={a:4} rejoue={b:4} "
          f"{d['question'][:50]}")

print(f"\nCONTROLE DE REPRODUCTION : {ok}/{total} verdicts identiques")
if ok >= 11:
    print("=> le bras A en banque sert de cote « avec plafond ». Rien a rejouer.")
    sys.exit(0)
print("=> seuil de 11/12 non atteint : le cote « avec plafond » sera rejoue en entier.")
sys.exit(1)
