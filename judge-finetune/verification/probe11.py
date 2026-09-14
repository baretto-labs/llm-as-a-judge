#!/usr/bin/env python3
"""Probes for batch_11 Python: analyse d'URL, jointure de chemins, comparaison de secrets."""
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse

print("── urlparse et validation d'origine")
cas = [
    "https://interne.example.com/api",
    "//evil.example.net/api",
    "https://evil.example.net@interne.example.com/api",
    "https://interne.example.com.evil.net/api",
    "http://interne.example.com/api",
    "https://INTERNE.example.com/api",
]
for url in cas:
    p = urlparse(url)
    print(f"   {url:<52} scheme={p.scheme or '(vide)':<6} netloc={p.netloc!r} hostname={p.hostname!r}")

print("   -> comparer netloc laisse passer l'info utilisateur ; hostname l'écarte et normalise la casse")

print("── urljoin et bases relatives")
base = "https://interne.example.com/api/v1/"
for suffixe in ["ressource", "/autre", "//evil.example.net/x", "https://evil.example.net/x"]:
    print(f"   urljoin(base, {suffixe!r:<28}) = {urljoin(base, suffixe)}")

print("── os.path.join et chemin absolu")
print(f"   os.path.join('/srv/data', 'rapport.txt') = {os.path.join('/srv/data', 'rapport.txt')}")
print(f"   os.path.join('/srv/data', '/etc/passwd') = {os.path.join('/srv/data', '/etc/passwd')}   <- la base est jetée")
print(f"   Path('/srv/data') / '/etc/passwd'        = {Path('/srv/data') / '/etc/passwd'}")
print(f"   normpath('/srv/data/../etc/passwd')      = {os.path.normpath('/srv/data/../etc/passwd')}")

racine = Path("/srv/data").resolve()
for demande in ["rapport.txt", "../etc/passwd", "/etc/passwd"]:
    cible = (racine / demande).resolve()
    dedans = racine == cible or racine in cible.parents
    print(f"   demande={demande!r:<16} -> {str(cible):<28} dans la racine ? {dedans}")

print("── comparaison de chaînes sensibles à la casse")
print(f"   'ADMIN'.lower() == 'admin'                 : {'ADMIN'.lower() == 'admin'}")
print(f"   'ADMİN'.lower() == 'admin'                 : {'ADMİN'.lower() == 'admin'}   <- I turc")
print(f"   'ADMİN'.casefold() == 'admin'              : {'ADMİN'.casefold() == 'admin'}")
print(f"   'ß'.lower() == 'ss' / 'ß'.casefold() == 'ss' : {'ß'.lower() == 'ss'} / {'ß'.casefold() == 'ss'}")
