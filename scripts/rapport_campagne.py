#!/usr/bin/env python3
"""Lit les fichiers jugés d'une campagne RAG et rend les mesures déclarées avant exécution.

    python3 scripts/rapport_campagne.py benchmarks/rag-campaign-juge-*.jsonl

Écrit le 2026-10-18, AVANT que le moindre jugement existe : les mesures et leur lecture sont
celles de `benchmarks/PREENREGISTREMENT_REPONSE.md` et de son amendement du même jour. Ce
script ne choisit rien ; il calcule ce qui a été déclaré.

Trois sorties, dans cet ordre :

  1. Par bras et par juge : taux de PASS du contexte, de la réponse, et les INVALID à part.
     Un INVALID n'est jamais fondu dans un FAIL — un juge qui n'a pas rendu de JSON
     exploitable n'a pas constaté un échec de la stratégie.

  2. McNemar exact bilatéral sur la PAIRE PRINCIPALE déclarée, vector ↔ vector-bm25, sur le
     verdict de contexte. Les paires discordantes sont publiées avec le p : à cet effectif
     c'est leur nombre qui détermine la puissance.

  3. Accord entre juges, κ de Cohen, quand plusieurs fichiers sont passés.
     CE N'EST PAS UNE JUSTESSE. Les réponses de la campagne RAG n'ont aucune étiquette de
     référence ; seul `judge-finetune/data/golden/test.jsonl` en a. Un désaccord dit que les
     deux juges divergent, jamais lequel a raison.

Python et non shell : κ et le binomial exact sont déjà définis une fois dans
`judge-finetune/scripts/benchmark_judges.py`, et ce script IMPORTE cette définition au lieu
d'en écrire une seconde. Deux définitions divergentes d'une même statistique publiée seraient
un défaut, pas une commodité.
"""

import importlib.util
import json
import math
import pathlib
import sys
from collections import Counter, defaultdict

RACINE = pathlib.Path(__file__).resolve().parent.parent
BENCH = RACINE / "judge-finetune" / "scripts" / "benchmark_judges.py"

_spec = importlib.util.spec_from_file_location("benchmark_judges", BENCH)
_bj = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bj)
cohen_kappa = _bj.cohen_kappa          # une seule définition dans le dépôt
INVALID = _bj.INVALID

ORDRE_BRAS = ["vector", "vector-bm25", "graphrag"]
PAIRE_PRINCIPALE = ("vector", "vector-bm25")


def charge(chemin):
    lignes = []
    for l in pathlib.Path(chemin).read_text().splitlines():
        if l.strip():
            lignes.append(json.loads(l))
    if not lignes:
        sys.exit(f"{chemin} est vide")
    etiquettes = {l["judgeLabel"] for l in lignes}
    if len(etiquettes) != 1:
        sys.exit(f"{chemin} mélange plusieurs juges : {etiquettes}")
    return etiquettes.pop(), lignes


def binomiale_exacte(b, c):
    """p bilatéral du test de McNemar exact : loi binomiale(b + c, 1/2)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    queue = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * queue)


def taux(lignes, champ, bras):
    sous = [l for l in lignes if l["arm"] == bras]
    if not sous:
        return None
    n = len(sous)
    p = sum(1 for l in sous if l[champ] == "PASS")
    inv = sum(1 for l in sous if l[champ] == INVALID)
    return n, p, inv


def table_par_bras(etiquette, lignes):
    print(f"\n── {etiquette} ─ taux de PASS par bras ─────────────────────────────")
    print(f"{'bras':<14}{'n':>5}{'contexte':>12}{'ctx INV.':>10}{'réponse':>12}{'rep INV.':>10}")
    for bras in ORDRE_BRAS:
        t = taux(lignes, "contextVerdict", bras)
        if t is None:
            continue
        n, pc, ic = t
        _, pr, ir = taux(lignes, "answerVerdict", bras)
        print(f"{bras:<14}{n:>5}{100*pc/n:>11.1f}%{ic:>10}{100*pr/n:>11.1f}%{ir:>10}")


def mcnemar(etiquette, lignes, champ, a, b):
    """Apparié sur la question : les deux bras ont répondu à la MÊME question."""
    par_question = defaultdict(dict)
    for l in lignes:
        par_question[l["question"]][l["arm"]] = l[champ]
    # Un INVALID d'un côté rend la paire inexploitable : exclue et comptée à part.
    exploitables, ecartees = [], 0
    for verdicts in par_question.values():
        if a not in verdicts or b not in verdicts:
            continue
        va, vb = verdicts[a], verdicts[b]
        if INVALID in (va, vb):
            ecartees += 1
            continue
        exploitables.append((va, vb))
    nb = sum(1 for va, vb in exploitables if va == "PASS" and vb == "FAIL")
    nc = sum(1 for va, vb in exploitables if va == "FAIL" and vb == "PASS")
    p = binomiale_exacte(nb, nc)
    pa = sum(1 for va, _ in exploitables if va == "PASS")
    pb = sum(1 for _, vb in exploitables if vb == "PASS")
    n = len(exploitables)
    print(f"\n── {etiquette} ─ McNemar {a} ↔ {b} ({champ}) ────────────────")
    if n == 0:
        print("  aucune paire exploitable")
        return
    ecart = 100 * pb / n - 100 * pa / n
    print(f"  paires exploitables : {n}   écartées pour INVALID : {ecartees}")
    print(f"  {a:<14}{100*pa/n:>6.1f}%   {b:<14}{100*pb/n:>6.1f}%   écart {ecart:+.1f} pts")
    print(f"  discordantes : {a} seul {nb}, {b} seul {nc}   p = {p:.4f}")
    # Lecture fixée d'avance : PREENREGISTREMENT_REPONSE.md § « Lecture fixée à l'avance ».
    if p < 0.05 and abs(ecart) >= 15:
        verdict = "le chiffre va à l'écran"
    elif p >= 0.05:
        verdict = "NON CONCLUANT — c'est le mot employé, pas l'estimation ponctuelle"
    else:
        verdict = "écart < 15 pts : rapporté brut, aucune affirmation à l'écran"
    print(f"  lecture déclarée : {verdict}")


def accord_entre_juges(campagnes):
    """κ entre deux juges sur les mêmes générations. Accord, PAS justesse."""
    print("\n── Accord entre juges ─────────────────────────────────────────────")
    print("  Rappel déclaré avant mesure : les réponses de la campagne RAG n'ont AUCUNE")
    print("  étiquette de référence. Ceci mesure la divergence des juges, jamais leur justesse.")
    noms = list(campagnes)
    for i in range(len(noms)):
        for j in range(i + 1, len(noms)):
            a, b = noms[i], noms[j]
            for champ in ("contextVerdict", "answerVerdict"):
                cle = lambda l: (l["arm"], l["question"])
                ma = {cle(l): l[champ] for l in campagnes[a]}
                mb = {cle(l): l[champ] for l in campagnes[b]}
                communs = sorted(set(ma) & set(mb))
                if not communs:
                    print(f"  {a} ↔ {b} ({champ}) : aucun item commun")
                    continue
                ga = [ma[k] for k in communs]
                gb = [mb[k] for k in communs]
                k = cohen_kappa(ga, gb)
                acc = 100 * sum(x == y for x, y in zip(ga, gb)) / len(communs)
                print(f"  {a} ↔ {b} ({champ:<14}) n={len(communs):<4} "
                      f"accord brut {acc:5.1f}%   κ = {k:.3f}")

    # Contrôle du point 2 de l'amendement du 2026-10-18 : l'ORDRE des bras.
    print("\n  Ordre des bras par taux de PASS du contexte, juge par juge :")
    ordres = {}
    for nom, lignes in campagnes.items():
        classement = sorted(
            (b for b in ORDRE_BRAS if any(l["arm"] == b for l in lignes)),
            key=lambda b: -taux(lignes, "contextVerdict", b)[1] / taux(lignes, "contextVerdict", b)[0])
        ordres[nom] = tuple(classement)
        print(f"    {nom:<20} {' > '.join(classement)}")
    if len(set(ordres.values())) == 1:
        print("  → même ordre chez tous les juges : la parenté de famille générateur/juge")
        print("    n'a pas porté le résultat. Le classement peut aller à l'écran.")
    else:
        print("  → les juges DIVERGENT sur l'ordre. Lecture déclarée : aucun classement à")
        print("    l'écran, le désaccord est publié tel quel et c'est lui qui se raconte.")


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    campagnes = {}
    for chemin in argv[1:]:
        etiquette, lignes = charge(chemin)
        campagnes[etiquette] = lignes
        table_par_bras(etiquette, lignes)
        mcnemar(etiquette, lignes, "contextVerdict", *PAIRE_PRINCIPALE)
        mcnemar(etiquette, lignes, "contextVerdict", "vector-bm25", "graphrag")
    if len(campagnes) > 1:
        accord_entre_juges(campagnes)
    else:
        print("\n(un seul juge : l'accord entre juges demande au moins deux fichiers)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
