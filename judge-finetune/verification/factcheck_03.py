#!/usr/bin/env python3
"""Fact-checks the Python claims of batch_03 (b03-007 IBAN, b03-008 dict comprehension)."""
import re

ok = lambda label, cond, detail="": print(f"{'OK ' if cond else 'KO '} {label} {detail}")

# ── b03-007 : la logique mod 97 de la réponse est correcte (seul `re` pose problème)
print("── b03-007")
_IBAN_FORMAT = re.compile(r"[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}")


def is_valid_iban(s: str) -> bool:
    if not _IBAN_FORMAT.fullmatch(s):
        return False
    rearranged = s[4:] + s[:4]
    digits = "".join(str(int(c, 36)) for c in rearranged)
    return int(digits) % 97 == 1


ok("IBAN de test valide (GB82WEST12345698765432)", is_valid_iban("GB82WEST12345698765432"))
ok("chiffre altéré -> False", not is_valid_iban("GB82WEST12345698765433"))
ok("clé altérée -> False", not is_valid_iban("GB83WEST12345698765432"))
ok("format trop court -> False", not is_valid_iban("GB82WEST1"))
ok("minuscules refusées", not is_valid_iban("gb82west12345698765432"))
ok("second IBAN valide (DE89370400440532013000)", is_valid_iban("DE89370400440532013000"))

# ── b03-008 : la compréhension est équivalente, doublons compris
print("── b03-008")
users = [
    {"email": "A@x.com", "active": True, "n": 1},
    {"email": "b@x.com", "active": False, "n": 2},
    {"email": "a@x.com", "active": True, "n": 3},
    {"email": "c@x.com", "active": True, "n": 4},
]

loop_result = {}
for user in users:
    if user["active"]:
        loop_result[user["email"].lower()] = user

comp_result = {u["email"].lower(): u for u in users if u["active"]}

ok("boucle et compréhension identiques", loop_result == comp_result)
ok("dernière occurrence conservée sur doublon", comp_result["a@x.com"]["n"] == 3,
   f"n={comp_result['a@x.com']['n']}")
ok("utilisateur inactif exclu", "b@x.com" not in comp_result)
ok("ordre des clés préservé", list(loop_result) == list(comp_result) == ["a@x.com", "c@x.com"],
   str(list(comp_result)))
