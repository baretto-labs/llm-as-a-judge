"""Lecture du banc plafond — règles figées dans benchmarks/PREENREGISTREMENT_PLAFOND.md.
Ce script n'invente aucun seuil : il applique ceux qui y sont écrits.

    python3 -I scripts/rapport_plafond.py
"""
import json, math, sys
from collections import defaultdict

BANQUE = "benchmarks/rag-campaign-juge-schema-coder32b.jsonl"
SANS = "benchmarks/plafond/sans-plafond.jsonl"
BRAS = ("vector", "vector-bm25", "graphrag")


def binomiale_exacte(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))


def mcnemar(titre, paires, nom_a, nom_b):
    nb = sum(1 for a, b in paires if a == "PASS" and b == "FAIL")
    nc = sum(1 for a, b in paires if a == "FAIL" and b == "PASS")
    n = len(paires)
    pa = sum(1 for a, _ in paires if a == "PASS")
    pb = sum(1 for _, b in paires if b == "PASS")
    p = binomiale_exacte(nb, nc)
    print(f"\n── {titre} ──────────────────────────────")
    print(f"  paires : {n}")
    print(f"  {nom_a:<22}{100*pa/n:>6.1f}%   {nom_b:<22}{100*pb/n:>6.1f}%   "
          f"écart {100*pb/n - 100*pa/n:+.1f} pts")
    print(f"  discordantes : {nom_a} seul {nb}, {nom_b} seul {nc}   p = {p:.4f}")
    return p, 100 * pb / n - 100 * pa / n


avec = {(d["arm"], d["question"]): d["contextVerdict"] for d in map(json.loads, open(BANQUE))}
sans_l = [json.loads(l) for l in open(SANS)]
echecs = sum(1 for d in sans_l if d["sortie"] is None)
sans = {(d["arm"], d["question"]): d["sortie"]["verdict"] for d in sans_l if d["sortie"]}
tronques = {k for k, d in ((( d["arm"], d["question"]), d) for d in sans_l)
            if d["caracteres"] > 6000}

print("═══ BANC PLAFOND — lecture pré-enregistrée ═══")
print(f"\nGarde-fou 1 — échecs : {echecs}/180 (annule le banc au-delà de 9)")
if echecs > 9:
    print("  => BANC ANNULÉ."); sys.exit(1)

intacts = [k for k in sans if k not in tronques]
change = [k for k in intacts if avec[k] != sans[k]]
print(f"Garde-fou 2 — déterminisme sur les {len(intacts)} contextes que le plafond ne "
      f"touchait pas : {len(change)} verdicts changent (annule le banc au-delà de 6)")
if len(change) > 6:
    print("  => BANC ANNULÉ."); sys.exit(1)
print(f"  contextes tronqués par le plafond : {len(tronques)}")

print("\n\n########## Q1 — PRINCIPALE : vector ↔ vector-bm25, SANS plafond ##########")
q = defaultdict(dict)
for (a, question), v in sans.items():
    q[question][a] = v
paires = [(d["vector"], d["vector-bm25"]) for d in q.values()
          if "vector" in d and "vector-bm25" in d]
p1, e1 = mcnemar("vector ↔ vector-bm25 (sans plafond)", paires, "vector", "vector-bm25")
print("  LECTURE DÉCLARÉE : " + ("paire CONCLUANTE — le chiffre va à l'écran, le plafond "
      "masquait l'écart" if p1 < 0.05 else
      "p ≥ 0,05 — à l'écran : « indiscernables, plafond ou pas ». C'est une mesure, pas une "
      "cécité ; elle REMPLACE la formulation actuelle."))

print("\n\n########## Q2 — l'effet du plafond lui-même ##########")
pt = [(avec[k], sans[k]) for k in sorted(tronques)]
p2, e2 = mcnemar(f"avec plafond ↔ sans plafond, sur les {len(pt)} contextes tronqués",
                 pt, "avec plafond", "sans plafond")
print("\n  bascules par bras RAG :")
for b in BRAS:
    sous = [k for k in tronques if k[0] == b]
    g = sum(1 for k in sous if avec[k] == "FAIL" and sans[k] == "PASS")
    pr = sum(1 for k in sous if avec[k] == "PASS" and sans[k] == "FAIL")
    print(f"    {b:<13} {len(sous):2} tronqués : {g} FAIL→PASS, {pr} PASS→FAIL")
print("  LECTURE DÉCLARÉE : brut (notes), sauf si Q1 bascule — dans ce cas il accompagne Q1 "
      "à l'écran." if p1 >= 0.05 else
      "  LECTURE DÉCLARÉE : Q1 bascule, ce résultat passe à l'écran avec elle.")

print("\n\n########## Q3 — SECONDAIRE : graphrag ↔ vector-bm25, SANS plafond ##########")
paires = [(d["vector-bm25"], d["graphrag"]) for d in q.values()
          if "vector-bm25" in d and "graphrag" in d]
p3, e3 = mcnemar("vector-bm25 ↔ graphrag (sans plafond)", paires, "vector-bm25", "graphrag")
print("  LECTURE DÉCLARÉE : " + ("sens conservé (graphrag en dessous) — la conclusion 4 "
      "reste à l'écran, chiffre mis à jour." if e3 < 0 else
      "SENS INVERSÉ — la conclusion 4 SORT de la présentation, sans discussion."))

print("\n\n── taux de PASS par bras, avec et sans plafond ──────────")
print(f"{'bras':<14}{'avec':>9}{'sans':>9}{'écart':>9}")
for b in BRAS:
    ks = [k for k in sans if k[0] == b]
    a_ = 100 * sum(avec[k] == "PASS" for k in ks) / len(ks)
    s_ = 100 * sum(sans[k] == "PASS" for k in ks) / len(ks)
    print(f"{b:<14}{a_:>8.1f}%{s_:>8.1f}%{s_-a_:>+8.1f}")
