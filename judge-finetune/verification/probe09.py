#!/usr/bin/env python3
"""Probes for batch_09 Python: injection de commande, coût quadratique, off-by-one sur tranches."""
import subprocess
import time

print("── subprocess : shell=True contre liste d'arguments")
nom_fichier = "rapport.txt; echo INJECTE"

res = subprocess.run(f"echo Traitement de {nom_fichier}", shell=True, capture_output=True, text=True)
print(f"   shell=True  -> sortie : {res.stdout.strip()!r}")
print(f"   shell=True  -> nombre de lignes produites : {len(res.stdout.strip().splitlines())}")

res2 = subprocess.run(["echo", "Traitement de", nom_fichier], capture_output=True, text=True)
print(f"   liste       -> sortie : {res2.stdout.strip()!r}")
print(f"   liste       -> nombre de lignes produites : {len(res2.stdout.strip().splitlines())}")

print("── appartenance : liste contre ensemble")
for taille in (2_000, 10_000, 50_000):
    valeurs = list(range(taille))
    cibles = list(range(0, taille, max(1, taille // 500)))

    t0 = time.perf_counter()
    trouves = sum(1 for c in cibles if c in valeurs)
    duree_liste = time.perf_counter() - t0

    ensemble = set(valeurs)
    t0 = time.perf_counter()
    trouves2 = sum(1 for c in cibles if c in ensemble)
    duree_ensemble = time.perf_counter() - t0

    rapport = duree_liste / duree_ensemble if duree_ensemble else float("inf")
    print(f"   n={taille:>6} | liste {duree_liste*1000:7.2f} ms | ensemble {duree_ensemble*1000:6.3f} ms "
          f"| rapport {rapport:6.0f}x | {trouves}=={trouves2}")

print("── tranches et bornes")
lignes = ["l0", "l1", "l2", "l3", "l4"]
print(f"   lignes[1:3]            = {lignes[1:3]}")
print(f"   lignes[0:len-1]        = {lignes[0:len(lignes) - 1]}   <- perd le dernier")
print(f"   lignes[10:20]          = {lignes[10:20]}   <- pas d'IndexError sur une tranche")
try:
    lignes[10]
except IndexError as e:
    print(f"   lignes[10]             -> IndexError : {e}")
print(f"   range(1, len(lignes))  = {list(range(1, len(lignes)))}   <- démarre à 1, saute l'élément 0")
print(f"   enumerate(start=1)     = {[(i, v) for i, v in enumerate(lignes[:2], start=1)]}")
