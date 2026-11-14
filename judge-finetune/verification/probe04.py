#!/usr/bin/env python3
"""Probes for batch_04 Python candidates: copies, floats/rounding, datetimes, mutation, regex."""
import copy
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

print("── copie superficielle vs profonde")
original = {"tags": ["a", "b"], "n": 1}
shallow = copy.copy(original)
deep = copy.deepcopy(original)
shallow["tags"].append("c")
print(f"   après append sur la copie superficielle : original={original}")
deep["tags"].append("d")
print(f"   après append sur la copie profonde      : original={original}")
print(f"   dict(original) partage aussi la liste ? {dict(original)['tags'] is original['tags']}")

print("── flottants et arrondis")
print(f"   0.1 + 0.2 == 0.3 ? {0.1 + 0.2 == 0.3}  (valeur={0.1 + 0.2!r})")
print(f"   round(2.675, 2) = {round(2.675, 2)}   (arrondi au pair le plus proche + binaire)")
print(f"   round(0.5) = {round(0.5)}, round(1.5) = {round(1.5)}, round(2.5) = {round(2.5)}")
print(f"   Decimal('2.675').quantize(0.01, HALF_UP) = {Decimal('2.675').quantize(Decimal('0.01'), ROUND_HALF_UP)}")
print(f"   sum([0.1]*10) == 1.0 ? {sum([0.1] * 10) == 1.0}  (valeur={sum([0.1] * 10)!r})")

print("── dates et fuseaux")
naive = datetime(2026, 3, 29, 2, 30)
paris = ZoneInfo("Europe/Paris")
aware = datetime(2026, 3, 28, 23, 30, tzinfo=timezone.utc)
print(f"   naïf sans fuseau : {naive} (tzinfo={naive.tzinfo})")
print(f"   même instant à Paris : {aware.astimezone(paris)}")
# passage à l'heure d'été 2026 : 2h -> 3h dans la nuit du 28 au 29 mars
before = datetime(2026, 3, 29, 1, 30, tzinfo=paris)
after = before + timedelta(hours=1)
print(f"   {before} + 1h = {after}  (offset {before.utcoffset()} -> {after.utcoffset()})")
print(f"   écart réel en UTC : {(after.astimezone(timezone.utc) - before.astimezone(timezone.utc))}")
try:
    datetime.utcnow()
    print(f"   datetime.utcnow() disponible (Python {sys.version_info.major}.{sys.version_info.minor})")
except Exception as e:  # pragma: no cover
    print(f"   datetime.utcnow() : {e}")

print("── mutation pendant l'itération")
nums = [1, 2, 3, 4, 5, 6]
for n in list(nums):
    pass
bad = [1, 2, 3, 4, 5, 6]
for n in bad:
    if n % 2 == 0:
        bad.remove(n)
print(f"   suppression pendant l'itération : {bad}  (attendu [1, 3, 5])")
good = [n for n in [1, 2, 3, 4, 5, 6] if n % 2]
print(f"   compréhension : {good}")

print("── retour arrière catastrophique")
pattern = re.compile(r"^(a+)+$")
for size in (18, 22, 24):
    text = "a" * size + "b"
    t0 = time.perf_counter()
    pattern.match(text)
    print(f"   (a+)+$ sur {size} 'a' + 'b' : {time.perf_counter() - t0:.3f} s")
t0 = time.perf_counter()
re.compile(r"^a+$").match("a" * 100000 + "b")
print(f"   a+$ sur 100000 'a' + 'b'   : {time.perf_counter() - t0:.4f} s")
