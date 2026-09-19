#!/usr/bin/env python3
"""Sweeps the corpus for surface features that predict the verdict.

Chantier 9 of AUDIT.md taught that a script only finds the correlations someone
thought to ask for: a fix for one surface leak silently created a worse one, which
survived a regeneration, a clean validation, three measurements and a commit.

So this sweeps many features at once, and — the part that matters — tests the
MAXIMUM over all of them against a permutation null of that same maximum. Reporting
the best of twenty searched features against a base rate is exactly the error that
once turned noise (p = 0.132) into an apparent +8.8 sigma.

    .venv/bin/python scripts/sweep_surface.py data/seed/*.jsonl
    .venv/bin/python scripts/sweep_surface.py --par-tache data/seed/*.jsonl
"""
import json
import random
import re
import sys
from collections import Counter

PERMUTATIONS = 2000
SEED = 17


def sections(msg, titre):
    """Extracts one '### TITRE' block out of the user message."""
    bloc = msg.split(f"### {titre}")
    if len(bloc) < 2:
        return ""
    reste = bloc[1]
    coupe = re.search(r"\n### ", reste)
    return reste[: coupe.start()] if coupe else reste


def traits(ex):
    """Surface features only: nothing here may look at the label or the reasoning."""
    user = ex["messages"][1]["content"]
    rep = sections(user, "SORTIE À ÉVALUER").strip()
    req = sections(user, "ENTREE / REQUÊTE").strip()
    ctx = sections(user, "CONTEXTE / RAG").strip()
    crit = sections(user, "CRITÈRES DE VALIDATION").strip()

    lignes = rep.split("\n")
    fences = rep.count("```")
    code = sum(len(b) for b in rep.split("```")[1::2])

    return {
        "reponse_caracteres": len(rep),
        "reponse_lignes": len(lignes),
        "reponse_mots": len(rep.split()),
        "reponse_ligne_moyenne": len(rep) / max(len(lignes), 1),
        "reponse_sections": rep.count("\n## ") + rep.startswith("## "),
        "reponse_blocs_code": fences // 2,
        "reponse_ratio_code": code / max(len(rep), 1),
        "reponse_puces": sum(1 for l in lignes if l.lstrip().startswith(("- ", "* "))),
        "reponse_liste_numerotee": sum(1 for l in lignes if re.match(r"^\s*\d+\. ", l)),
        "reponse_tableau": int("|---" in rep or "| ---" in rep),
        "reponse_gras": rep.count("**") // 2,
        "reponse_backticks": rep.count("`"),
        "reponse_chiffres": sum(c.isdigit() for c in rep),
        "reponse_commence_titre": int(rep.startswith("#")),
        "reponse_finit_code": int(rep.rstrip().endswith("```")),
        "reponse_deux_points": rep.count(" : "),
        "requete_caracteres": len(req),
        "requete_lignes": len(req.split("\n")),
        "requete_a_code": int("```" in req),
        "requete_gras": req.count("**") // 2,
        "contexte_caracteres": len(ctx),
        "criteres_nombre": len(re.findall(r"^\d+\. ", crit, re.M)),
    }


def meilleure_coupe(valeurs, y):
    """Best accuracy achievable by thresholding this feature, both directions.

    Uses prefix sums over the sorted order so a permutation costs O(n), not O(n*seuils).
    """
    n = len(y)
    ordre = sorted(range(n), key=lambda i: valeurs[i])
    cum, total = [0], 0
    for i in ordre:
        total += y[i]
        cum.append(total)
    positifs = cum[n]
    meilleur, seuil, sens = 0.0, None, None
    for k in range(n + 1):
        # Une coupe n'est réalisable qu'à une frontière d'ex æquo : sur un trait entier à
        # six valeurs, couper au milieu d'un groupe égal ne correspond à aucun seuil, et
        # gonfle la précision mesurée. Ce garde-fou manquait au premier jet.
        if 0 < k < n and valeurs[ordre[k - 1]] == valeurs[ordre[k]]:
            continue
        # k premiers prédits 0, le reste prédit 1
        justes = (k - cum[k]) + (positifs - cum[k])
        v = valeurs[ordre[k]] if k < n else None
        for acc, s in ((justes / n, ">="), ((n - justes) / n, "<")):
            if acc > meilleur:
                meilleur, seuil, sens = acc, v, s
    # La règle est rapportée telle qu'elle se lit : « trait <sens> <seuil> ⇒ PASS ».
    return meilleur, seuil, sens


def balayer(exemples, titre):
    noms = list(traits(exemples[0]))
    X = {nom: [traits(ex)[nom] for ex in exemples] for nom in noms}
    y = [1 if json.loads(ex["messages"][-1]["content"].split("</thinking>")[1])["verdict"] == "PASS"
         else 0 for ex in exemples]
    n = len(y)
    base = max(sum(y), n - sum(y)) / n

    observes = {nom: meilleure_coupe(X[nom], y) for nom in noms}
    max_observe = max(acc for acc, _, _ in observes.values())

    rng = random.Random(SEED)
    nuls = []
    for _ in range(PERMUTATIONS):
        melange = y[:]
        rng.shuffle(melange)
        nuls.append(max(meilleure_coupe(X[nom], melange)[0] for nom in noms))

    p_global = sum(1 for v in nuls if v >= max_observe) / PERMUTATIONS
    nuls_tries = sorted(nuls)
    seuil95 = nuls_tries[int(0.95 * PERMUTATIONS)]

    print(f"\n{'=' * 78}\n{titre}  —  {n} exemples, {sum(y)} PASS / {n - sum(y)} FAIL")
    print("=" * 78)
    print(f"  taux de base (classe majoritaire)     : {base:.1%}")
    print(f"  meilleur trait, toutes coupes         : {max_observe:.1%}")
    print(f"  null de permutation du MÊME maximum   : moyenne {sum(nuls)/len(nuls):.1%}, "
          f"95e centile {seuil95:.1%}")
    print(f"  p (maximum sur {len(noms)} traits)              : {p_global:.4f}")
    verdict = ("FUITE — un trait de surface sépare les verdicts au-delà du hasard"
               if p_global < 0.05 else
               "RAS — le meilleur trait ne fait pas mieux que le hasard, à 20 traits cherchés")
    print(f"  >>> {verdict}")

    print(f"\n  détail (à lire seulement si p global < 0,05) :")
    for nom, (acc, seuil, sens) in sorted(observes.items(), key=lambda kv: -kv[1][0])[:8]:
        marque = " <<<" if acc == max_observe else ""
        regle = f"« {nom} {sens} {seuil} ⇒ PASS »" if seuil is not None else "(aucune coupe)"
        print(f"    {nom:26} {acc:6.1%}  {regle}{marque}")
    return p_global


def main(argv):
    par_tache = "--par-tache" in argv
    fichiers = [a for a in argv if not a.startswith("--")]
    if not fichiers:
        sys.exit("usage: sweep_surface.py [--par-tache] <lots.jsonl...>")

    exemples = []
    for f in fichiers:
        with open(f) as fh:
            exemples += [json.loads(l) for l in fh if l.strip()]

    p = balayer(exemples, "CORPUS ENTIER")
    if par_tache:
        for tache, n in Counter(ex["meta"]["task"] for ex in exemples).most_common():
            sous = [ex for ex in exemples if ex["meta"]["task"] == tache]
            if len(sous) >= 20:
                balayer(sous, f"TÂCHE {tache}")
    return 1 if p < 0.05 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
