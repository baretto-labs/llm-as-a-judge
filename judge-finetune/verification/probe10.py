#!/usr/bin/env python3
"""Probes for batch_10 Python: __eq__ sans __hash__, dataclass frozen, tri par clé."""
from dataclasses import dataclass, FrozenInstanceError

print("── __eq__ sans __hash__")


class PointNu:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, autre):
        return isinstance(autre, PointNu) and (self.x, self.y) == (autre.x, autre.y)


class PointOk:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, autre):
        return isinstance(autre, PointOk) and (self.x, self.y) == (autre.x, autre.y)

    def __hash__(self):
        return hash((self.x, self.y))


print(f"   PointNu(1,2) == PointNu(1,2) : {PointNu(1, 2) == PointNu(1, 2)}")
print(f"   __hash__ de PointNu          : {PointNu.__hash__}")
try:
    {PointNu(1, 2)}
except TypeError as e:
    print(f"   set(PointNu)                 : TypeError — {e}")
print(f"   set de deux PointOk égaux    : taille {len({PointOk(1, 2), PointOk(1, 2)})}")


class SansEq:
    pass


print(f"   classe sans __eq__ : hachable ? {SansEq() in {SansEq()} or True} (hash hérité d'object conservé)")

print("── dataclass frozen et eq")


@dataclass(frozen=True)
class Config:
    hote: str
    port: int


c = Config("localhost", 8080)
print(f"   frozen : hachable ? {isinstance(hash(c), int)} | égalité par valeur ? {c == Config('localhost', 8080)}")
try:
    c.port = 9090
except FrozenInstanceError as e:
    print(f"   mutation : FrozenInstanceError — {e}")


@dataclass(eq=True)
class ConfigMutable:
    hote: str


print(f"   dataclass(eq=True) non frozen : __hash__ = {ConfigMutable.__hash__}")
try:
    {ConfigMutable('a')}
except TypeError as e:
    print(f"   set(dataclass eq non frozen) : TypeError — {e}")

print("── tri par clé et stabilité")
articles = [("b", 2), ("a", 1), ("c", 2), ("d", 1)]
print(f"   sorted(key=quantité)      : {sorted(articles, key=lambda t: t[1])}")
print(f"   sorted(key=(quantité,nom)) : {sorted(articles, key=lambda t: (t[1], t[0]))}")
print(f"   sorted(reverse=True) sur clé composite : {sorted(articles, key=lambda t: (t[1], t[0]), reverse=True)}")
