"""Lecture du banc échelle, telle que fixée dans benchmarks/PREENREGISTREMENT_ECHELLE.md.
Aucun seuil n'est choisi ici."""
import json, sys, collections, statistics as st

SEUIL_PASS = 7      # fixé avant mesure
VIVANTE = 5         # une valeur est « vivante » si elle apparaît >= 5 fois sur 180

r = [json.loads(l) for l in open(sys.argv[1])]
ech = [x for x in r if x["sortie"] is None]
print(f"{len(r)} jugements, {len(ech)} en échec")
if len(ech) > 9:
    print("=> BANC ANNULÉ : plus de 9 échecs, garde-fou déclaré."); sys.exit(0)
ok = [x for x in r if x["sortie"]]

print("\n── Q1 DISPERSION ───────────────────────────────")
c = collections.Counter(x["sortie"]["note"] for x in ok)
for n in range(11):
    if c[n]:
        print(f"  note {n:2} : {c[n]:3}  {'█' * (c[n] * 40 // len(ok))}")
viv = sorted(n for n in c if c[n] >= VIVANTE)
print(f"  valeurs vivantes (>= {VIVANTE} occurrences) : {len(viv)}/11  -> {viv}")
print("  lecture déclarée : " + ("le chiffre va à l'écran" if len(viv) <= 4
      else "chiffre brut, aucune leçon" if len(viv) <= 6 else "rien ne va à l'écran"))

print("\n── Q2 DÉCISION, contre le verdict binaire ──────")
ref = {(d["arm"], d["question"]): d["contextVerdict"]
       for d in map(json.loads, open("benchmarks/rag-campaign-juge-schema-coder32b.jsonl"))}
paires = [(ref[(x["arm"], x["question"])],
           "PASS" if x["sortie"]["note"] >= SEUIL_PASS else "FAIL") for x in ok]
acc = sum(a == b for a, b in paires)
po = acc / len(paires)
pa = sum((sum(a == v for a, _ in paires) / len(paires)) * (sum(b == v for _, b in paires) / len(paires))
         for v in ("PASS", "FAIL"))
print(f"  accord brut {po*100:.1f}%   κ = {(po-pa)/(1-pa):.3f}   désaccords {len(paires)-acc}/{len(paires)}")
print("  (description, aucune phrase d'écran n'en dépend)")

print("\n── Q3 CLASSEMENT ───────────────────────────────")
moy = {}
for a in ("vector", "vector-bm25", "graphrag"):
    n = [x["sortie"]["note"] for x in ok if x["arm"] == a]
    moy[a] = st.mean(n)
    print(f"  {a:12} note moyenne {moy[a]:5.2f}   médiane {st.median(n):4.1f}   n={len(n)}")
ordre = " > ".join(sorted(moy, key=moy.get, reverse=True))
print(f"  ordre par la note    : {ordre}")
print(f"  ordre par le verdict : vector > vector-bm25 > graphrag")
print("  lecture déclarée : " + ("la concordance va à l'écran"
      if ordre == "vector > vector-bm25 > graphrag"
      else "ordres différents -> aucun classement n'est présenté comme établi"))
