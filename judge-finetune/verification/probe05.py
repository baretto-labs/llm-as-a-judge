#!/usr/bin/env python3
"""Probes for batch_05 Python: encodage, division, stabilité du tri, versions, __slots__."""
import locale
import sys
import tempfile
from pathlib import Path

print("── encodage par défaut")
print(f"   locale.getpreferredencoding(False) = {locale.getpreferredencoding(False)}")
print(f"   sys.getdefaultencoding()           = {sys.getdefaultencoding()}")
print(f"   sys.flags.utf8_mode                = {sys.flags.utf8_mode}")
tmp = Path(tempfile.mkdtemp()) / "accents.txt"
tmp.write_text("café — naïve\n", encoding="utf-8")
print(f"   relecture sans encoding= : {open(tmp).read()!r}")
try:
    print(f"   relecture en latin-1     : {open(tmp, encoding='latin-1').read()!r}")
except UnicodeDecodeError as e:
    print(f"   relecture en latin-1     : UnicodeDecodeError {e}")
try:
    open(tmp, encoding="ascii").read()
except UnicodeDecodeError as e:
    print(f"   relecture en ascii       : UnicodeDecodeError ({e.reason})")

print("── division et arrondi")
print(f"   7 // 2 = {7 // 2} | -7 // 2 = {-7 // 2} | int(-3.5) = {int(-3.5)} | -7 % 2 = {-7 % 2}")
print(f"   7 / 2  = {7 / 2}  | divmod(-7, 2) = {divmod(-7, 2)}")

print("── stabilité du tri")
staff = [("R&D", "Ana"), ("Ops", "Bob"), ("R&D", "Cid"), ("Ops", "Dan")]
print(f"   sorted par dept : {sorted(staff, key=lambda e: e[0])}")
print(f"   tri en deux passes (nom puis dept) : "
      f"{sorted(sorted(staff, key=lambda e: e[1]), key=lambda e: e[0])}")

print("── comparaison de versions")
versions = ["1.9.0", "1.10.0", "1.2.0"]
print(f"   tri lexicographique : {sorted(versions)}")
print(f"   tri par tuple       : {sorted(versions, key=lambda v: tuple(int(p) for p in v.split('.')))}")
print(f"   '1.10' > '1.9' ? {'1.10' > '1.9'}  (chaînes)")

print("── __slots__")


class WithDict:
    def __init__(self, x, y):
        self.x, self.y = x, y


class WithSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


a, b = WithDict(1, 2), WithSlots(1, 2)
size_dict = sys.getsizeof(a) + sys.getsizeof(a.__dict__)
size_slots = sys.getsizeof(b)
print(f"   instance + __dict__ : {size_dict} octets")
print(f"   instance __slots__  : {size_slots} octets")
try:
    b.z = 3
    print("   attribut hors slots : accepté")
except AttributeError as e:
    print(f"   attribut hors slots : AttributeError — {e}")
