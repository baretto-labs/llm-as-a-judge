#!/usr/bin/env python3
"""Vérifie que chaque expectedFqnHint de QuestionCorpus existe vraiment dans la codebase.

Un indice qui ne correspond à rien est une cible que `hintCoverage` ne pourra jamais
atteindre : la métrique déterministe — la seule qui ne passe pas par un LLM — se met
alors à plafonner sous 1.0 sans que rien ne le signale.

Trois statuts, du plus fort au plus faible :

  DECLARE  le nom est déclaré dans le source (classe, interface, enum, record,
           méthode, constante, champ). C'est ce qu'on veut.
  PRESENT  le nom apparaît dans le texte des fichiers mais n'est déclaré nulle part :
           import d'un type externe, mot d'un commentaire, fragment d'une chaîne.
           Acceptable pour un type de bibliothèque, suspect pour le reste.
  ABSENT   introuvable. Défaut franc.

Le statut qui fait foi est ABSENT. PRESENT n'est PAS un défaut du corpus : c'est une
limite connue de la détection par expressions régulières, et elle est documentée ici pour
qu'on ne rejoue pas une hypothèse déjà réfutée.

Angles morts mesurés le 2026-09-21, sur les 30 questions d'origine :

  - Une méthode d'interface dont les paramètres portent des annotations à parenthèses
    échappe à la détection : `TokenStream chat(@V("systemPrompt") String s, ...)` — la
    regex s'arrête sur la parenthèse de `@V(`. C'est le cas de `chat` et `refactor`.
    Une première tentative de correctif, fondée sur l'idée que les méthodes d'interface
    étaient ratées faute de corps, n'a **rien changé** : l'hypothèse était fausse.
  - Certaines méthodes privées ordinaires échappent aussi, par rétro-action de la regex
    principale (`calculateDynamicThreshold`).
  - Les types de `java.lang` ne sont jamais importés, donc jamais classés EXTERNE
    (`AutoCloseable`).

Chasser la syntaxe Java à coups de regex a un rendement décroissant. Ce que ce script
doit garantir, il le garantit : aucun indice ne nomme quelque chose qui n'existe pas.

Usage :
  python3 scripts/verify_question_hints.py [chemin/vers/src/main/java]
"""
import pathlib
import re
import sys
from collections import Counter

DEFAUT = pathlib.Path.home() / "Workspaces/Labs/OllamAssist/src/main/java"
CORPUS = pathlib.Path("src/test/java/fr/baretto/benchmarks/jmh/QuestionCorpus.java")

DECL_TYPE = re.compile(r"\b(?:class|interface|enum|record|@interface)\s+(\w+)")
DECL_METHODE = re.compile(r"\b(?:public|private|protected|static|final|synchronized|abstract|native|\s)+"
                          r"[\w<>\[\],.?\s]+\s+(\w+)\s*\([^;]*\)\s*(?:\{|throws)")
DECL_CHAMP = re.compile(r"\b(?:public|private|protected|static|final|volatile|transient|\s)+"
                        r"[\w<>\[\],.?\s]+\s+(\w+)\s*(?:=|;)")
# Angle mort de la première version : une méthode d'interface ou abstraite n'a pas de
# corps, donc la regex exigeant `{` ou `throws` les ratait toutes — `chat` et `refactor`
# de l'interface `Assistant` ressortaient en PRESENT alors qu'elles y sont déclarées.
DECL_METHODE_ABSTRAITE = re.compile(r"[\w<>\[\],.?]\s+(\w+)\s*\([^;{)]*\)\s*;")
# Constantes d'enum et composants de record, également invisibles jusqu'ici.
DECL_ENUM = re.compile(r"^\s*([A-Z][A-Z0-9_]{2,})\s*[,;(]", re.M)
DECL_RECORD = re.compile(r"\brecord\s+\w+\s*\(([^)]*)\)", re.S)


IMPORTE = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;", re.M)


def indexe(racine: pathlib.Path):
    """Retourne (déclarés, texte global, importés, nb fichiers), tout en minuscules."""
    declares, textes, importes, fichiers = set(), [], set(), 0
    for f in racine.rglob("*.java"):
        src = f.read_text(encoding="utf-8", errors="replace")
        fichiers += 1
        textes.append(src)
        for rx in (DECL_TYPE, DECL_METHODE, DECL_CHAMP, DECL_METHODE_ABSTRAITE, DECL_ENUM):
            declares.update(m.lower() for m in rx.findall(src))
        for fqn in IMPORTE.findall(src):
            importes.add(fqn.rsplit(".", 1)[-1].lower())
        for params in DECL_RECORD.findall(src):
            declares.update(m.lower() for m in re.findall(r"(\w+)\s*(?:,|$)", params))
    return declares, "\n".join(textes).lower(), importes, fichiers


SANS_COMMENTAIRE = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)


def questions(chemin: pathlib.Path):
    src = chemin.read_text(encoding="utf-8")
    attendu = src.count("new Question(")

    # Les commentaires sont retirés AVANT l'analyse. Sans cela, une ligne `//` glissée
    # entre `Difficulty.X,` et `new String[]{` fait disparaître la question du relevé,
    # en silence : le `\s*` de la regex ne traverse pas un commentaire. C'est arrivé le
    # 2026-09-21, en documentant une correction d'indice — le script a annoncé
    # « 0 absent » sur 29 questions au lieu de 30, la question défectueuse n'étant plus lue.
    src = SANS_COMMENTAIRE.sub("", src)

    blocs = re.findall(
        r"new Question\(\s*\"(.*?)\",\s*Difficulty\.(\w+),\s*new String\[\]\{(.*?)\}",
        src, re.S)

    # Garde-fou : analyser moins de questions qu'il n'y en a doit être une ERREUR, jamais
    # un relevé partiel. Un sous-ensemble silencieux produit un « aucun absent » qui ne
    # veut rien dire.
    if len(blocs) != attendu:
        sys.exit(f"[ERREUR] {len(blocs)} questions analysées pour {attendu} occurrences de "
                 f"`new Question(`. L'analyse en perd — ne pas se fier au résultat.")

    for texte, diff, bruts in blocs:
        yield texte, diff, re.findall(r'"([^"]+)"', bruts)


def main():
    racine = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAUT
    if not racine.is_dir():
        sys.exit(f"[ERREUR] codebase introuvable : {racine}")
    if not CORPUS.is_file():
        sys.exit(f"[ERREUR] corpus introuvable : {CORPUS} (lancer depuis la racine du dépôt)")

    declares, texte_global, importes, fichiers = indexe(racine)
    print(f"codebase : {racine}")
    print(f"  {fichiers} fichiers, {len(declares)} identifiants déclarés\n")

    statuts, absents, presents_seuls = Counter(), [], []
    total_q = 0
    for texte, diff, hints in questions(CORPUS):
        total_q += 1
        detail = []
        for h in hints:
            hl = h.lower()
            if hl in declares:
                st = "DECLARE"
            elif hl in importes:
                st = "EXTERNE"
            elif hl in texte_global:
                st = "PRESENT"
            else:
                st = "ABSENT"
            statuts[st] += 1
            detail.append((h, st))
            if st == "ABSENT":
                absents.append((texte, h))
            elif st == "PRESENT":
                presents_seuls.append((texte, h))
        faibles = [f"{h}:{s}" for h, s in detail if s not in ("DECLARE", "EXTERNE")]
        if faibles:
            print(f"  [{diff:<12}] {texte[:62]}")
            print(f"       {'  '.join(faibles)}")

    total = sum(statuts.values())
    print(f"\n{total_q} questions, {total} indices")
    for st in ("DECLARE", "EXTERNE", "PRESENT", "ABSENT"):
        n = statuts[st]
        print(f"  {st:<8} {n:>3}  ({n / total:.0%})")

    if absents:
        print(f"\nABSENTS — {len(absents)}, à corriger :")
        for q, h in absents:
            print(f"  {h!r}  dans : {q[:70]}")
    else:
        print("\naucun indice absent")

    return 1 if absents else 0


if __name__ == "__main__":
    sys.exit(main())
