"""Lecture du banc notation, telle que fixée dans benchmarks/PREENREGISTREMENT_NOTATION.md.
Aucun seuil n'est choisi ici : ils viennent du pré-enregistrement."""
import json, sys, collections, itertools

SEUIL_PASS = 7  # note >= 7 => PASS, fixé avant la mesure
r = [json.loads(l) for l in open(sys.argv[1])]

def decision(rec):
    s = rec["sortie"]
    if s is None:
        return None
    return s["verdict"] if "verdict" in s else ("PASS" if s["note"] >= SEUIL_PASS else "FAIL")

err = [x for x in r if x["sortie"] is None]
print(f"{len(r)} jugements, {len(err)} en échec")

temoin = collections.Counter()
for (i, f), g in itertools.groupby(sorted([x for x in r if x["genre"] == "temoin"],
                                            key=lambda x: (x["item"], x["format"])),
                                     key=lambda x: (x["item"], x["format"])):
    d = {decision(x) for x in g}
    if len(d) > 1:
        temoin[f] += 1
print(f"\nTÉMOIN (2 passes à ordre identique) — retournements : "
      f"binaire {temoin['binaire']}, note {temoin['note']}")
if temoin["binaire"] or temoin["note"]:
    print("=> EXPÉRIENCE INVALIDE selon le pré-enregistrement : service non déterministe.")
    sys.exit(0)
print("=> témoin propre, la lecture s'applique.")

inst = {}
for f in ("binaire", "note"):
    n = 0
    for i in sorted({x["item"] for x in r}):
        d = {decision(x) for x in r if x["item"] == i and x["format"] == f and x["genre"] == "permute"}
        if len(d) > 1:
            n += 1
    inst[f] = n
A, B = inst["binaire"], inst["note"]
print(f"\nRETOURNEMENTS DE DÉCISION sur 3 permutations, 12 items :")
print(f"  A binaire : {A}/12")
print(f"  B note    : {B}/12   (seuil PASS >= {SEUIL_PASS})")

if A == 0:
    verdict = ("le chiffre va à l'écran" if B >= 3 else
               "chiffre brut, aucune leçon" if B >= 1 else "rien ne va à l'écran")
    print(f"  A = 0, règle du seuil absolu => {verdict}")
else:
    verdict = ("le chiffre va à l'écran" if B >= 3 * A else
               "chiffre brut, aucune leçon" if B > A else "rien ne va à l'écran")
    print(f"  B/A = {B/A:.2f} => {verdict}")

print("\nCOULEUR (jamais seule à l'écran) — dispersion des notes par item :")
gros = 0
for i in sorted({x["item"] for x in r}):
    n = [x["sortie"]["note"] for x in r
         if x["item"] == i and x["format"] == "note" and x["genre"] == "permute" and x["sortie"]]
    if n:
        d = max(n) - min(n)
        gros += d >= 2
        print(f"  item {i+1:2} notes {sorted(n)} amplitude {d}")
print(f"  items dont la note varie d'au moins 2 points : {gros}/12")
