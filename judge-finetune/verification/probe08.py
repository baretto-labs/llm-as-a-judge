#!/usr/bin/env python3
"""Probes for batch_08 Python: désérialisation pickle, imports circulaires, dataclass mutable."""
import pickle
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

print("── désérialisation pickle")


class Charge:
    def __reduce__(self):
        # __reduce__ dit à pickle comment reconstruire l'objet : n'importe quel appelable convient.
        return (print, ("   [charge exécutée pendant pickle.loads]",))


donnees = pickle.dumps(Charge())
print(f"   taille du flux : {len(donnees)} octets, aucune exécution à la sérialisation")
print("   appel de pickle.loads :")
pickle.loads(donnees)
print("   -> aucune exception, aucun avertissement")

try:
    import json
    json.loads('{"a": 1}')
    print("   json.loads sur la même intention : impossible, le format ne porte pas d'appelable")
except Exception as e:  # pragma: no cover
    print(f"   json : {e}")

print("── imports circulaires")
tmp = Path(tempfile.mkdtemp())
(tmp / "a.py").write_text("import b\n\ndef fa():\n    return b.fb()\n\nVALEUR_A = 'a'\n", encoding="utf-8")
(tmp / "b.py").write_text("import a\n\nVALEUR_B = a.VALEUR_A\n\ndef fb():\n    return 'b'\n", encoding="utf-8")
(tmp / "main.py").write_text("import a\nprint('   import réussi :', a.fa())\n", encoding="utf-8")
res = subprocess.run([sys.executable, "main.py"], cwd=tmp, capture_output=True, text=True)
print(f"   code de retour : {res.returncode}")
for ligne in (res.stdout + res.stderr).strip().splitlines()[-3:]:
    print(f"   {ligne.strip()}")

# variante : import différé dans la fonction
(tmp / "b.py").write_text("def fb():\n    import a\n    return a.VALEUR_A + 'b'\n", encoding="utf-8")
res2 = subprocess.run([sys.executable, "main.py"], cwd=tmp, capture_output=True, text=True)
print(f"   avec import différé dans la fonction -> code {res2.returncode} : {res2.stdout.strip()}")

print("── dataclass et valeur par défaut mutable")
try:
    @dataclass
    class PanierKo:
        articles: list = []
    print("   liste nue en défaut : acceptée")
except ValueError as e:
    print(f"   liste nue en défaut : ValueError — {e}")


@dataclass
class PanierOk:
    articles: list = field(default_factory=list)


p1, p2 = PanierOk(), PanierOk()
p1.articles.append("pomme")
print(f"   default_factory : p1={p1.articles} p2={p2.articles} partagé ? {p1.articles is p2.articles}")
