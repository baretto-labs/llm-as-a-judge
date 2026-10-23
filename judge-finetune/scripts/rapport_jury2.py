#!/usr/bin/env python3
"""Dépouillement du jury à trois familles — PREENREGISTREMENT_JURY2.md.

Écrit AVANT que Gemma ait rendu un verdict. N'applique que les trois lectures
déclarées, et refuse de conclure si un garde-fou tombe. Réutilise l'extraction
de verdict du harnais : aucune seconde logique de lecture ne peut diverger.

    .venv/bin/python -I scripts/rapport_jury2.py
"""
import collections, glob, importlib.util, json, os, sys
from math import comb
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
os.chdir(RACINE)
spec = importlib.util.spec_from_file_location("bj", "scripts/benchmark_judges.py")
bj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bj)

JURY = {
    "Qwen":    "32B-baseline-conventions",
    "Mistral": "Mistral-24B-baseline-conventions",
    "Google":  "Gemma-4-31B-baseline-conventions",
}
COMPARATEUR = "32B-baseline-conventions"   # 45/50 — déclaré comme seul comparateur
ALPHA = 0.05
SEUIL_INVALIDES = 15        # sur 150 jugements ; > 15 ⇒ variante annulée
PLAFOND_SORTIE = 2048       # amendement du 2026-10-20 20h48 : > 0 sortie au plafond ⇒ annulée
PASSES = 3


def binomiale_exacte(b, c):
    """McNemar exact bilatéral, et test binomial du sens des erreurs."""
    n = b + c
    if n == 0:
        return 1.0
    k = max(b, c)
    queue = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * queue)


def charge(nom):
    """Verdict par item, vote majoritaire sur les passes — la règle du harnais."""
    chemin = f"results/runs/{nom}.jsonl"
    if not Path(chemin).exists():
        return None, None, None
    brut = collections.defaultdict(list)
    lignes = au_plafond = 0
    for ligne in open(chemin, encoding="utf-8"):
        o = json.loads(ligne)
        lignes += 1
        if o.get("error"):
            continue
        if (o.get("completion_tokens") or 0) >= PLAFOND_SORTIE:
            au_plafond += 1
        j = bj.extract_judgment(o.get("text") or "")
        if j and j.get("verdict"):
            brut[o["id"]].append(j["verdict"])
    verdicts = {i: collections.Counter(v).most_common(1)[0][0] for i, v in brut.items()}
    invalides = lignes - sum(len(v) for v in brut.values())
    return verdicts, invalides, au_plafond


def sens(etalon, verdicts):
    doux = sum(1 for i, g in etalon.items() if g == "FAIL" and verdicts.get(i) == "PASS")
    dur  = sum(1 for i, g in etalon.items() if g == "PASS" and verdicts.get(i) == "FAIL")
    return doux, dur


def main():
    etalon = {g["id"]: g["gold"]["verdict"] for g in bj.load_golden("data/golden/test.jsonl")}
    print(f"Étalon : {len(etalon)} items, " + str(dict(collections.Counter(etalon.values()))))

    votes, manquants = {}, []
    for famille, nom in JURY.items():
        v, inv, plafond = charge(nom)
        if v is None:
            manquants.append(nom)
            continue
        print(f"  {famille:8s} {nom:34s} {len(v)} items, {inv} non extractibles sur {PASSES*len(etalon)}"
              f", {plafond} au plafond {PLAFOND_SORTIE}")
        if plafond > 0:
            sys.exit(f"\nGARDE-FOU (amendement du 2026-10-20 20h48) : {nom} rend {plafond} sortie(s) "
                     f"atteignant {PLAFOND_SORTIE} jetons.\nLecture déclarée : la variante est annulée. "
                     f"Le plafond NE SERA PAS monté une seconde fois.")
        if inv > SEUIL_INVALIDES:
            sys.exit(f"\nGARDE-FOU : {nom} rend {inv} verdits non extractibles (> {SEUIL_INVALIDES}).\n"
                     f"Lecture déclarée : la variante est annulée et N'EST PAS LUE. JURY2 ne rend rien.")
        votes[famille] = v
    if manquants:
        sys.exit(f"\nRun absent : {', '.join(manquants)} — rien n'est dépouillé.")

    # ── Vote majoritaire des trois familles, une voix chacune ────────────────
    jury = {}
    for i in etalon:
        vs = [v[i] for v in votes.values() if i in v]
        if len(vs) < len(JURY):
            continue
        jury[i] = collections.Counter(vs).most_common(1)[0][0]
    seul = votes["Qwen"]

    j_ok = sum(1 for i, g in etalon.items() if jury.get(i) == g)
    s_ok = sum(1 for i, g in etalon.items() if seul.get(i) == g)
    n = len(jury)

    # ── Q1 — principale ──────────────────────────────────────────────────────
    b = sum(1 for i, g in etalon.items() if i in jury and jury[i] == g and seul.get(i) != g)
    c = sum(1 for i, g in etalon.items() if i in jury and jury[i] != g and seul.get(i) == g)
    p1 = binomiale_exacte(b, c)
    print(f"\n## Q1 — le jury bat-il le meilleur juge seul ?\n")
    print(f"  jury (3 familles) {j_ok}/{n} = {j_ok/n:.0%}")
    print(f"  {COMPARATEUR} seul {s_ok}/{len(etalon)} = {s_ok/len(etalon):.0%}")
    print(f"  discordantes : jury seul juste {b}, juge seul juste {c} — McNemar exact p = {p1:.4f}")
    if j_ok > s_ok and p1 < ALPHA:
        print("  LECTURE DÉCLARÉE : le jury GAGNE. Le chiffre va à l'écran, la diapo 29 est réécrite.")
    elif j_ok <= s_ok:
        print("  LECTURE DÉCLARÉE : ajouter des votants N'AIDE PAS. Le chiffre va à l'écran tel quel,")
        print("                     quelle que soit la valeur de p.")
    else:
        print("  LECTURE DÉCLARÉE : NON CONCLUANT. C'est le mot qui va à l'écran, pas l'estimation.")

    # ── Q2 — l'indulgence est-elle une propriété de la famille ? ─────────────
    print(f"\n## Q2 — sens des erreurs, par famille\n")
    for famille, v in votes.items():
        doux, dur = sens(etalon, v)
        p = binomiale_exacte(doux, dur)
        print(f"  {famille:8s} indulgent {doux:2d} / sévère {dur:2d}   p = {p:.4f}")
    doux, dur = sens(etalon, votes["Google"])
    p2 = binomiale_exacte(doux, dur)
    if doux > dur and p2 < ALPHA:
        print("\n  LECTURE DÉCLARÉE : trois familles sans ancêtre commun, le MÊME biais.")
        print("                     La phrase va à l'écran.")
    elif doux > dur:
        print("\n  LECTURE DÉCLARÉE : sens rapporté brut, SANS la phrase (p ≥ 0,05).")
    else:
        print("\n  LECTURE DÉCLARÉE : l'observation du 20/10 NE GÉNÉRALISE PAS.")
        print("                     Ce résultat va à l'écran AUSSI, et affaiblit la leçon n° 5.")

    # ── Q3 — descriptive ─────────────────────────────────────────────────────
    doux, dur = sens(etalon, jury)
    print(f"\n## Q3 — sens des erreurs du jury (descriptif, aucun seuil)\n")
    print(f"  indulgentes {doux}, sévères {dur}, sur {n - j_ok} erreurs")


if __name__ == "__main__":
    main()
