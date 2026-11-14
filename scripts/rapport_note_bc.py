"""Lecture des bras B et C — règles figées dans benchmarks/PREENREGISTREMENT_NOTE_BC.md.
Binarisation déclarée AVANT la mesure : note >= 7 vaut PASS. Aucun autre seuil n'est essayé.

    python3 -I scripts/rapport_note_bc.py
"""
import json, sys
from collections import Counter

BANQUE = "benchmarks/rag-campaign-juge-schema-coder32b.jsonl"
SEUIL = 7           # déclaré au pré-enregistrement
VIVANTE = 5         # une note « vivante » apparaît au moins 5 fois sur 180
BRAS = ("vector", "vector-bm25", "graphrag")

A = {(d["arm"], d["question"]): d["contextVerdict"] for d in map(json.loads, open(BANQUE))}
jeux = {}
for nom, f in (("B", "benchmarks/notation/bras-B.jsonl"),
               ("C", "benchmarks/notation/bras-C.jsonl")):
    lignes = [json.loads(l) for l in open(f)]
    echecs = sum(1 for d in lignes if d["sortie"] is None)
    print(f"Garde-fou — bras {nom} : {echecs}/180 échecs (annule le bras au-delà de 9)")
    if echecs > 9:
        print(f"  => BRAS {nom} ANNULÉ, non lu.")
        continue
    jeux[nom] = {(d["arm"], d["question"]): d["sortie"]["note"] for d in lignes if d["sortie"]}
if not jeux:
    sys.exit(1)


def kappa(paires):
    n = len(paires)
    po = sum(a == b for a, b in paires) / n
    pa = sum((sum(a == v for a, _ in paires) / n) * (sum(b == v for _, b in paires) / n)
             for v in {x for p in paires for x in p})
    return po, (po - pa) / (1 - pa) if pa < 1 else float("nan")


print("\n\n########## Q1 — PRINCIPALE : l'échelle à 11 niveaux en a-t-elle 11 ? ##########")
for nom, notes in jeux.items():
    c = Counter(notes.values())
    vives = sorted(v for v, k in c.items() if k >= VIVANTE)
    print(f"\n  bras {nom} — distribution sur {len(notes)} jugements :")
    print("    " + "  ".join(f"{v}×{c[v]}" for v in sorted(c)))
    print(f"    valeurs vivantes (≥{VIVANTE} occurrences) : {len(vives)}  {vives}")
    lecture = ("le chiffre VA À L'ÉCRAN" if len(vives) <= 4 else
               "brut (notes), pas écran" if len(vives) <= 6 else
               "RIEN à l'écran : l'échelle se tient, la leçon n'existe pas")
    print(f"    LECTURE DÉCLARÉE : {lecture}")

print("\n\n########## Q2 — la note décide-t-elle comme le binaire ? ##########")
for nom, notes in jeux.items():
    paires = [("PASS" if n >= SEUIL else "FAIL", A[k]) for k, n in notes.items() if k in A]
    po, k = kappa(paires)
    d = sum(1 for a, b in paires if a != b)
    print(f"  bras {nom} (note ≥ {SEUIL}) contre le verdict de A : accord brut {po*100:.1f}%  "
          f"κ = {k:.3f}  désaccords {d}/{len(paires)}")

print("\n\n########## Q3 — la note classe-t-elle les trois bras comme le verdict ? ##########")
ordre_A = sorted(BRAS, key=lambda b: -100 * sum(
    A[k] == "PASS" for k in A if k[0] == b) / sum(1 for k in A if k[0] == b))
print(f"  ordre rendu par le verdict binaire de A : {' > '.join(ordre_A)}")
for b in BRAS:
    ks = [k for k in A if k[0] == b]
    print(f"    {b:<13} PASS {100*sum(A[k]=='PASS' for k in ks)/len(ks):5.1f}%")
memes = True
for nom, notes in jeux.items():
    moy = {b: sum(n for k, n in notes.items() if k[0] == b) /
              sum(1 for k in notes if k[0] == b) for b in BRAS}
    ordre = sorted(BRAS, key=lambda b: -moy[b])
    memes &= ordre == ordre_A
    print(f"\n  bras {nom} — note moyenne : " +
          "   ".join(f"{b} {moy[b]:.2f}" for b in BRAS))
    print(f"    ordre : {' > '.join(ordre)}   {'IDENTIQUE à A' if ordre == ordre_A else 'DIFFÉRENT de A'}")
print("\n  LECTURE DÉCLARÉE : " + ("même ordre partout — phrase à l'écran : la note coûte "
      "plus cher et décide pareil." if memes and len(jeux) == 2 else
      "ordre différent quelque part — brut, et la phrase est interdite."))

print("\n\n########## Q4 — les critères changent-ils quelque chose ? (B contre C) ##########")
if len(jeux) == 2:
    communs = [k for k in jeux["B"] if k in jeux["C"]]
    po, k = kappa([(jeux["B"][x], jeux["C"][x]) for x in communs])
    mb = sum(jeux["B"][x] for x in communs) / len(communs)
    mc = sum(jeux["C"][x] for x in communs) / len(communs)
    vb = len([v for v, n in Counter(jeux["B"].values()).items() if n >= VIVANTE])
    vc = len([v for v, n in Counter(jeux["C"].values()).items() if n >= VIVANTE])
    print(f"  notes identiques : {po*100:.1f}%   κ(B,C) = {k:.3f}   sur {len(communs)} items")
    print(f"  note moyenne : B {mb:.2f}   C {mc:.2f}   écart {mc-mb:+.2f}")
    print(f"  valeurs vivantes : B {vb}   C {vc}")
    pob, kb = kappa([("PASS" if jeux["B"][x] >= SEUIL else "FAIL",
                      "PASS" if jeux["C"][x] >= SEUIL else "FAIL") for x in communs])
    print(f"  une fois binarisées à {SEUIL} : accord {pob*100:.1f}%   κ = {kb:.3f}")
