#!/usr/bin/env python3
"""Probes for batch_06 Python: comparaison à temps constant, attribut de classe mutable,
cycles et gc, lecture intégrale contre itération ligne à ligne."""
import gc
import hmac
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path

print("── comparaison de secrets")
secret = "a" * 64


def timed(fn, arg, runs=20000):
    samples = []
    for _ in range(5):
        t0 = time.perf_counter()
        for _ in range(runs):
            fn(secret, arg)
        samples.append(time.perf_counter() - t0)
    return statistics.median(samples)


early = "b" + "a" * 63          # diffère au 1er caractère
late = "a" * 63 + "b"           # diffère au dernier
print(f"   ==            , diff. au 1er car. : {timed(lambda a, b: a == b, early)*1e3:.2f} ms")
print(f"   ==            , diff. au dernier  : {timed(lambda a, b: a == b, late)*1e3:.2f} ms")
print(f"   compare_digest, diff. au 1er car. : {timed(hmac.compare_digest, early)*1e3:.2f} ms")
print(f"   compare_digest, diff. au dernier  : {timed(hmac.compare_digest, late)*1e3:.2f} ms")

print("── attribut de classe mutable")


class Basket:
    items = []          # partagé par toutes les instances

    def add(self, item):
        self.items.append(item)


class BasketOk:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)


a, b = Basket(), Basket()
a.add("pomme")
print(f"   attribut de classe : a.items={a.items} | b.items={b.items} | partagé ? {a.items is b.items}")
c, d = BasketOk(), BasketOk()
c.add("pomme")
print(f"   attribut d'instance: c.items={c.items} | d.items={d.items} | partagé ? {c.items is d.items}")

print("── cycles de références")


class Node:
    def __init__(self, name):
        self.name = name
        self.peer = None

    def __del__(self):
        print(f"   __del__ appelé pour {self.name}")


x, y = Node("x"), Node("y")
x.peer, y.peer = y, x
del x, y
print(f"   après del, objets encore vivants ? collecte manuelle -> {gc.collect()} objets récupérés")

print("── lecture d'un fichier volumineux")
path = Path(tempfile.mkdtemp()) / "gros.txt"
with path.open("w", encoding="utf-8") as f:
    for i in range(200_000):
        f.write(f"ligne {i} " + "x" * 40 + "\n")
print(f"   taille du fichier : {path.stat().st_size / 1e6:.1f} Mo")

tracemalloc.start()
with path.open(encoding="utf-8") as f:
    content = f.read()
    total = sum(1 for line in content.splitlines() if line.startswith("ligne 1"))
peak_all = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
del content

tracemalloc.start()
with path.open(encoding="utf-8") as f:
    total2 = sum(1 for line in f if line.startswith("ligne 1"))
peak_iter = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
print(f"   read() intégral      : pic {peak_all / 1e6:.1f} Mo (résultat {total})")
print(f"   itération ligne à ligne : pic {peak_iter / 1e6:.3f} Mo (résultat {total2})")
