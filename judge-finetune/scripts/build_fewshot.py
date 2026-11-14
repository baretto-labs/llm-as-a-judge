#!/usr/bin/env python3
"""Fabrique configs/conventions-fewshot.md depuis data/mlx/train.jsonl.

Le fichier produit n'est JAMAIS édité à la main : il se régénère par
`make fewshot`, comme les lots de data/seed/. Toute modification passe par la
règle de sélection ci-dessous, qui est déclarée dans PREENREGISTREMENT_FEWSHOT.md.

RÈGLE DE SÉLECTION, gelée le 2026-10-17 avant toute génération
--------------------------------------------------------------
Six exemples, un par couple (tâche, verdict) pour les trois tâches du banc.
Dans chaque couple, le PREMIER item `cas == "limite"` en ordre de fichier.

Pourquoi les cas limites et non un panachage : la variante à conventions rend
déjà 76 % de justesse, c'est-à-dire qu'elle tranche correctement les cas francs.
Ce que les critiques sont censées transmettre, c'est l'arbitrage des cas
ambigus — là où l'accord avec l'étalon s'effondre (κ 0,48). Un bloc d'exemples
francs n'enseignerait que ce qui est déjà acquis.

Risque déclaré : un juge n'ayant vu que des cas limites peut devenir erratique
sur les cas francs. La justesse du banc le révélera, elle couvre les deux.

CLOISONNEMENT
-------------
Les exemples viennent EXCLUSIVEMENT de data/mlx/train.jsonl. Les 50 items de
data/golden/test.jsonl ne peuvent pas y entrer : le tirage `make split` est
disjoint, et un exemple du test dans l'invite rendrait la mesure sans valeur.
Le script le vérifie et s'arrête plutôt que de produire un fichier douteux.

LES CRITIQUES NE SONT PAS ÉCRITES PAR UN HUMAIN
-----------------------------------------------
Le bloc <thinking> de chaque exemple vient du corpus, dont les étiquettes sont
produites par un modèle (data/REVUE_GOLDEN.md, en-tête). La méthode de Husain
suppose des critiques écrites par l'expert du domaine. Ici elles ne le sont pas,
et aucune des six n'a été relue — la relecture en aveugle a porté sur les 50
items du test, pas sur le train. C'est une divergence avec la méthode, pas une
approximation : elle est déclarée dans le pré-enregistrement et se dira à l'oral.
"""
import glob
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
TRAIN = RACINE / "data/mlx/train.jsonl"
TEST = RACINE / "data/golden/test.jsonl"
CONVENTIONS = RACINE / "configs/conventions.md"
SORTIE = RACINE / "configs/conventions-fewshot.md"

TACHES = ["CODE_ANALYSIS", "RAG_CONTEXT_RELEVANCE", "RAG_FAITHFULNESS"]
VERDICTS = ["PASS", "FAIL"]


def lignes(p):
    return [json.loads(l) for l in p.open(encoding="utf-8")]


def meta_par_enonce():
    """data/mlx/*.jsonl ne porte que `messages` ; les identifiants sont dans les lots seed."""
    index = {}
    for p in sorted(glob.glob(str(RACINE / "data/seed/batch_*.jsonl"))):
        for l in open(p, encoding="utf-8"):
            d = json.loads(l)
            index[d["messages"][1]["content"]] = d["meta"]
    return index


def verdict_de(row):
    return json.loads(row["messages"][-1]["content"].split("</thinking>")[-1].strip())["verdict"]


def tache_de(row):
    return row["messages"][0]["content"].split("TÂCHE:")[1].split(".")[0].strip()


def main():
    index = meta_par_enonce()
    train = lignes(TRAIN)

    enonces_test = {t["messages"][1]["content"] for t in lignes(TEST)}
    ids_test = {index[e]["id"] for e in enonces_test if e in index}

    choix = {}
    for row in train:
        cle = (tache_de(row), verdict_de(row))
        m = index[row["messages"][1]["content"]]
        if cle not in choix and m.get("cas") == "limite":
            choix[cle] = (row, m)

    attendus = [(t, v) for t in TACHES for v in VERDICTS]
    manquants = [c for c in attendus if c not in choix]
    if manquants:
        sys.exit(f"[ERREUR] aucun cas limite pour : {manquants}. La règle de sélection ne tient plus.")

    blocs, ids = [], []
    for cle in attendus:
        row, m = choix[cle]
        if m["id"] in ids_test:
            sys.exit(f"[ERREUR] fuite : {m['id']} est dans le golden set. Le banc serait sans valeur.")
        ids.append(m["id"])
        blocs.append(
            f"### EXEMPLE {len(ids)} — tâche {cle[0]}, cas limite, verdict attendu {cle[1]}\n\n"
            f"{row['messages'][1]['content'].strip()}\n\n"
            f"--- JUGEMENT ATTENDU, AVEC SON RAISONNEMENT ---\n\n"
            f"{row['messages'][-1]['content'].strip()}"
        )

    texte = (
        CONVENTIONS.read_text(encoding="utf-8").strip()
        + "\n\nEXEMPLES DE JUGEMENTS, AVEC LE RAISONNEMENT QUI LES JUSTIFIE\n\n"
        + "Six cas limites déjà tranchés. Ils montrent comment les conventions\n"
        + "ci-dessus s'appliquent quand le cas n'est pas franc. Juge l'item qui\n"
        + "t'est soumis de la même façon ; ne recopie aucun de ces verdicts.\n\n"
        + "\n\n".join(blocs)
        + "\n"
    )
    SORTIE.write_text(texte, encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} : {len(texte)} caractères, 6 exemples")
    print("identifiants gelés :", " ".join(ids))


if __name__ == "__main__":
    main()
