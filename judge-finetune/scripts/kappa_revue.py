#!/usr/bin/env python3
"""Extract the first-pass annotations from REVUE_GOLDEN.md and compute agreement.

The review was conducted item by item in a markdown journal; that journal is the
ONLY machine-readable trace of the annotator's first pass. Rather than
transcribing 50 entries by hand -- the exact failure mode this project forbids
for the JSONL -- the tables are parsed here, and the parse is checked against
tallies recorded independently while the review ran.

A failing cross-check means the parser is wrong, not the tallies. Do not relax
an assertion to make this script pass. The first version of this script silently
returned 42 items out of 50 and missed all three `citations_exactes`
disagreements; the cross-checks are what caught it.

What counts as the two passes
-----------------------------
annotator : the FIRST blind pass only. `annotateur, après révélation` rows are
            excluded -- they are a second reading, taken after the label was
            shown, and folding them in would inflate agreement.
label     : the label AS PRESENTED at review time, which is what the blind pass
            was actually compared against. The rows headed `étiquette
            d'origine` and `étiquette (corrigée le matin même)` are therefore
            read exactly like plain `étiquette` rows. Labels corrected as a
            RESULT of the review are outcomes of the review, not its yardstick.

Journal shapes this has to survive
----------------------------------
- headers carrying 3 or 4 checks, with or without a trailing `verdict` column
  (`b09-009` has none: its verdict is derived from the checks and stated in prose)
- row labels `annotateur, premier passage`, `annotateur, **premier passage**`
  and a bare `annotateur`
- cells written `V`, `F`, bolded, or `—` where the annotator gave no per-check
  mark (`b07-011`, which was answered with a verdict alone)
"""

from __future__ import annotations

import json
import pathlib
import random
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
JOURNAL = RACINE / "data" / "REVUE_GOLDEN.md"
GOLDEN = RACINE / "data" / "golden" / "test.jsonl"

# Recoupements notés au fil de la relecture, avant tout calcul groupé.
# La reference est l'etiquette TELLE QUE PRESENTEE : 47/50. Le journal tenait
# son decompte courant a 48/50 en creditant `b13-004` de la correction que la
# relecture avait elle-meme provoquee ; ce second chiffre est rapporte a part.
ATTENDU_ACCORD_VERDICT = 47
ATTENDU_ACCORD_APRES_CORRECTION = 48
ATTENDU_DESACCORDS_VERDICT = {"b07-011", "b12-007", "b13-004"}
ATTENDU_DESACCORDS_CITATIONS = {"b13-012", "b13-008", "b12-011"}

# Trois tables du journal abregent `exactitude_technique` en `exactitude`
# (`b07-011`, `b09-009`, `b10-015`). Verifie avant d'aliaser : aucun controle
# nomme `exactitude` n'existe dans le corpus, et aucun commit ne l'a renomme.
ALIAS_CONTROLES = {"exactitude": "exactitude_technique"}

EN_TETE_ITEM = re.compile(r"^###\s+\d+\.\s+`([a-z0-9]+-\d+)`")
VIDE = {"—", "-", "–", ""}


def cellules(ligne: str) -> list[str]:
    """Split a markdown row, dropping the empty edges and bold markers."""
    brut = ligne.strip().strip("|").split("|")
    return [c.replace("*", "").replace("`", "").strip() for c in brut]


def role(libelle: str) -> str | None:
    """Classify a row by its first cell. None = not a pass we score."""
    l = libelle.lower()
    if l.startswith("annotateur"):
        # Second lecture, faite apres revelation de l'etiquette : hors kappa.
        return None if "après révélation" in l else "annotateur"
    if l.startswith("étiquette"):
        return "etiquette"
    return None


def lire_journal() -> tuple[dict[str, dict], list[str]]:
    lignes = JOURNAL.read_text(encoding="utf-8").splitlines()
    releve: dict[str, dict] = {}
    anomalies: list[str] = []
    courant: str | None = None
    noms: list[str] | None = None
    porte_verdict = False

    for i, ligne in enumerate(lignes):
        entete = EN_TETE_ITEM.match(ligne)
        if entete:
            courant, noms = entete.group(1), None
            continue
        if not ligne.startswith("|"):
            continue

        # En-tete de tableau : premiere cellule vide, les suivantes nomment les controles.
        cols = cellules(ligne)
        if cols and cols[0] == "" and len(cols) > 2:
            bruts = [re.sub(r"^\d+\s+", "", c) for c in cols[1:]]
            porte_verdict = bool(bruts) and bruts[-1].lower() == "verdict"
            noms = [
                ALIAS_CONTROLES.get(n, n)
                for n in (bruts[:-1] if porte_verdict else bruts)
            ]
            continue

        if courant is None or noms is None:
            continue
        r = role(cols[0])
        if r is None:
            continue

        attendu = len(noms) + (1 if porte_verdict else 0)
        if len(cols) - 1 != attendu:
            anomalies.append(
                f"{courant} ligne {i + 1} : {len(cols) - 1} cellules pour {attendu} attendues"
            )
            continue

        valeurs = cols[1 : 1 + len(noms)]
        checks = {n: (v == "V") for n, v in zip(noms, valeurs) if v not in VIDE}

        if porte_verdict:
            verdict = cols[-1].upper()
        elif len(checks) == len(noms):
            verdict = "PASS" if all(checks.values()) else "FAIL"
        else:
            anomalies.append(f"{courant} ligne {i + 1} : verdict indeterminable")
            continue
        if verdict not in ("PASS", "FAIL"):
            anomalies.append(f"{courant} ligne {i + 1} : verdict illisible « {verdict} »")
            continue

        # Un item peut porter plusieurs lignes d'un meme role : la premiere fait foi.
        cible = releve.setdefault(courant, {})
        donnees = {"checks": checks, "verdict": verdict, "ligne": i + 1}
        if r == "etiquette" and "etiquette" in cible:
            # Seconde ligne d'etiquette : c'est la correction issue de la
            # relecture (`b13-004`), pas l'etiquette presentee. Elle ne sert
            # qu'au decompte secondaire. Distinguer par la position, non par le
            # libelle : `b03-005` porte « étiquette (corrigée le matin même) »,
            # qui est bien l'etiquette presentee.
            cible.setdefault("etiquette_apres_correction", donnees)
        else:
            cible.setdefault(r, donnees)

    return releve, anomalies


def kappa(a: list[str], b: list[str]) -> float:
    """Cohen's kappa on two aligned sequences of categorical labels."""
    n = len(a)
    if n == 0:
        return float("nan")
    accord = sum(x == y for x, y in zip(a, b)) / n
    hasard = sum((a.count(c) / n) * (b.count(c) / n) for c in set(a) | set(b))
    return float("nan") if hasard == 1.0 else (accord - hasard) / (1 - hasard)


def bootstrap(a: list[str], b: list[str], tirages: int = 10000, graine: int = 11):
    rng = random.Random(graine)
    n = len(a)
    ech = []
    for _ in range(tirages):
        idx = [rng.randrange(n) for _ in range(n)]
        k = kappa([a[i] for i in idx], [b[i] for i in idx])
        if k == k:  # ecarte les tirages degeneres (marge constante)
            ech.append(k)
    if not ech:
        return float("nan"), float("nan"), 0
    ech.sort()
    bas = ech[int(0.025 * len(ech))]
    haut = ech[min(int(0.975 * len(ech)), len(ech) - 1)]
    return bas, haut, len(ech)


def main() -> int:
    golden = {}
    for l in GOLDEN.open(encoding="utf-8"):
        d = json.loads(l)
        etq = json.loads(d["messages"][-1]["content"].split("</thinking>")[1])
        golden[d["meta"]["id"]] = {"meta": d["meta"], "checks": etq["checks"]}

    releve, anomalies = lire_journal()
    complets = {i: v for i, v in releve.items() if "annotateur" in v and "etiquette" in v}

    print(f"golden : {len(golden)} items    journal : {len(complets)} items apparies")
    if anomalies:
        print("\nlignes ecartees par le parseur :")
        for a in anomalies:
            print(f"  - {a}")

    ecarts = []
    absents = sorted(set(golden) - set(complets))
    intrus = sorted(set(complets) - set(golden))
    if absents:
        ecarts.append(f"items du golden absents du journal : {absents}")
    if intrus:
        ecarts.append(f"items du journal hors golden : {intrus}")

    # Recoupement fort : les controles nommes au journal doivent etre ceux de
    # l'etiquette. Un en-tete mal aligne se trahit ici, pas dans le kappa.
    for i in sorted(set(complets) & set(golden)):
        attendus = set(golden[i]["checks"])
        vus = set(complets[i]["etiquette"]["checks"]) | set(complets[i]["annotateur"]["checks"])
        if not vus <= attendus:
            ecarts.append(f"{i} : controles {sorted(vus - attendus)} inconnus de l'etiquette")

    desaccords_v = {
        i for i, v in complets.items()
        if v["annotateur"]["verdict"] != v["etiquette"]["verdict"]
    }
    if desaccords_v != ATTENDU_DESACCORDS_VERDICT:
        ecarts.append(
            f"desaccords verdict {sorted(desaccords_v)} au lieu de "
            f"{sorted(ATTENDU_DESACCORDS_VERDICT)}"
        )

    desaccords_c = {
        i for i, v in complets.items()
        if "citations_exactes" in v["annotateur"]["checks"]
        and "citations_exactes" in v["etiquette"]["checks"]
        and v["annotateur"]["checks"]["citations_exactes"]
        != v["etiquette"]["checks"]["citations_exactes"]
    }
    if desaccords_c != ATTENDU_DESACCORDS_CITATIONS:
        ecarts.append(
            f"desaccords citations_exactes {sorted(desaccords_c)} au lieu de "
            f"{sorted(ATTENDU_DESACCORDS_CITATIONS)}"
        )

    if ecarts:
        print("\nRECOUPEMENT EN ECHEC — le parseur est suspect, pas les decomptes :")
        for e in ecarts:
            print(f"  - {e}")
        return 1
    print("recoupements : OK (appariement, noms de controles, desaccords verdict et citations)")

    ids = sorted(complets)
    va = [complets[i]["annotateur"]["verdict"] for i in ids]
    ve = [complets[i]["etiquette"]["verdict"] for i in ids]
    accord = sum(x == y for x, y in zip(va, ve))
    if accord != ATTENDU_ACCORD_VERDICT:
        print(f"\nRECOUPEMENT EN ECHEC : accord {accord}, {ATTENDU_ACCORD_VERDICT} attendu")
        return 1

    k = kappa(va, ve)
    bas, haut, n_ech = bootstrap(va, ve)
    print(f"\nVERDICT  n={len(ids)}")
    print(f"  accord brut : {accord}/{len(ids)} = {accord / len(ids):.3f}")
    print(f"  kappa       : {k:.3f}   IC95% bootstrap [{bas:.3f}, {haut:.3f}]  ({n_ech} tirages retenus)")
    print(f"  marges      : annotateur {va.count('PASS')}P/{va.count('FAIL')}F    "
          f"etiquette {ve.count('PASS')}P/{ve.count('FAIL')}F")
    desaccords = [i for i in ids if complets[i]["annotateur"]["verdict"]
                  != complets[i]["etiquette"]["verdict"]]
    print(f"  desaccords  : {desaccords}")

    # Decompte secondaire : etiquette apres les corrections issues de la
    # relecture. Il credite l'etiquette d'un changement que l'annotateur a
    # provoque, donc il surestime l'accord ; publie pour memoire, jamais seul.
    vc = [
        complets[i].get("etiquette_apres_correction", complets[i]["etiquette"])["verdict"]
        for i in ids
    ]
    accord_c = sum(x == y for x, y in zip(va, vc))
    kc = kappa(va, vc)
    bas_c, haut_c, _ = bootstrap(va, vc)
    if accord_c != ATTENDU_ACCORD_APRES_CORRECTION:
        print(f"\nRECOUPEMENT EN ECHEC : accord apres correction {accord_c}, "
              f"{ATTENDU_ACCORD_APRES_CORRECTION} attendu")
        return 1
    print(f"\n  pour memoire, contre l'etiquette APRES correction :")
    print(f"    accord {accord_c}/{len(ids)}   kappa {kc:.3f}  IC95% [{bas_c:.3f}, {haut_c:.3f}]")
    print(f"    ecart du au seul b13-004, dont la relecture a change le verdict.")

    controles: dict[str, list[tuple[bool, bool]]] = {}
    for i in ids:
        ea = complets[i]["annotateur"]["checks"]
        ee = complets[i]["etiquette"]["checks"]
        for nom in ee:
            if nom in ea:
                controles.setdefault(nom, []).append((ea[nom], ee[nom]))

    print("\nPAR CONTROLE  (sur les items qui le portent et dont les deux passages sont marques)")
    for nom in sorted(controles, key=lambda n: (-len(controles[n]), n)):
        paires = controles[nom]
        a = ["V" if x else "F" for x, _ in paires]
        b = ["V" if y else "F" for _, y in paires]
        acc = sum(x == y for x, y in zip(a, b))
        kc = kappa(a, b)
        kc_txt = "n/d" if kc != kc else f"{kc:+.3f}"
        print(f"  {nom:<28} n={len(paires):>3}   accord {acc:>3}/{len(paires):<3}  kappa {kc_txt}")
    print("  n/d = marge degeneree (un controle constant chez l'un des deux passages) :")
    print("        l'accord brut reste lisible, le kappa n'est pas defini.")

    sortie = RACINE / "mesures" / "revue_annotateur.json"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(
        json.dumps(
            {
                "source": "data/REVUE_GOLDEN.md",
                "extrait_par": "scripts/kappa_revue.py",
                "definition": {
                    "annotateur": "premier passage en aveugle ; lignes « après révélation » exclues",
                    "etiquette": "l'etiquette telle que presentee lors de la lecture en aveugle",
                },
                "n": len(ids),
                "accord_verdict": accord,
                "kappa_verdict": k,
                "ic95_bootstrap": [bas, haut],
                "items": {i: complets[i] for i in ids},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nreleve ecrit : {sortie.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
