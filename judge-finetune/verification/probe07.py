#!/usr/bin/env python3
"""Probes for batch_07 Python: générateurs épuisés, décorateurs, transactions sqlite3."""
import functools
import sqlite3
import tempfile
from pathlib import Path

print("── générateur épuisé")


def lignes_valides(lignes):
    return (l.strip() for l in lignes if l.strip())


source = ["a", "  ", "b", "", "c"]
gen = lignes_valides(source)
total = sum(1 for _ in gen)
restant = list(gen)
print(f"   premier parcours : {total} éléments")
print(f"   second parcours  : {restant}  <- le générateur est épuisé")
print(f"   len(générateur)  : ", end="")
try:
    len(lignes_valides(source))
except TypeError as e:
    print(f"TypeError — {e}")

liste = [l.strip() for l in source if l.strip()]
print(f"   version liste    : {len(liste)} éléments, reparcourable : {liste}")

print("── décorateur sans functools.wraps")


def chrono_sans_wraps(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def chrono_avec_wraps(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


@chrono_sans_wraps
def calculer_tva(montant):
    """Calcule la TVA à 20 %."""
    return montant * 0.2


@chrono_avec_wraps
def calculer_tva_ok(montant):
    """Calcule la TVA à 20 %."""
    return montant * 0.2


print(f"   sans wraps : __name__={calculer_tva.__name__!r}, __doc__={calculer_tva.__doc__!r}")
print(f"   avec wraps : __name__={calculer_tva_ok.__name__!r}, __doc__={calculer_tva_ok.__doc__!r}")

print("── transactions sqlite3")
path = Path(tempfile.mkdtemp()) / "t.db"

conn = sqlite3.connect(path)
conn.execute("CREATE TABLE compte (id INTEGER PRIMARY KEY, solde INTEGER)")
conn.execute("INSERT INTO compte VALUES (1, 100)")
conn.close()
verif = sqlite3.connect(path)
print(f"   INSERT sans commit puis close() : {verif.execute('SELECT COUNT(*) FROM compte').fetchone()[0]} ligne(s)")
verif.close()

conn = sqlite3.connect(path)
conn.execute("INSERT INTO compte VALUES (2, 200)")
conn.commit()
conn.close()
verif = sqlite3.connect(path)
print(f"   INSERT avec commit              : {verif.execute('SELECT COUNT(*) FROM compte').fetchone()[0]} ligne(s)")
verif.close()

conn = sqlite3.connect(path)
try:
    with conn:                                   # commit à la sortie, rollback si exception
        conn.execute("UPDATE compte SET solde = solde - 50 WHERE id = 2")
        raise RuntimeError("échec métier au milieu de la transaction")
except RuntimeError:
    pass
solde = conn.execute("SELECT solde FROM compte WHERE id = 2").fetchone()[0]
print(f"   `with conn:` + exception        : solde = {solde} (attendu 200, rollback effectif)")
print(f"   isolation_level par défaut      : {conn.isolation_level!r}")
conn.close()
