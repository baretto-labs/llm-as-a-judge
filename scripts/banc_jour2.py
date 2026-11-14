"""Bancs du 2026-10-20 — dispositifs figés dans benchmarks/PREENREGISTREMENT_PLAFOND.md
et benchmarks/PREENREGISTREMENT_NOTE_BC.md.

    python3 -I scripts/banc_jour2.py <mode> <sortie.jsonl>
    mode : repro | temoin | plafond | B | C

Un seul script pour les quatre passes : elles ne diffèrent que par trois réglages (plafond,
critères dans l'invite, forme de la sortie) et doivent partager mot pour mot le reste de
l'invite, sans quoi la comparaison ne mesurerait pas ce qu'elle prétend.

Python et non shell : réplique de `Collections.shuffle` de Java, assemblage des schémas JSON,
reprise de l'invite de RagContextJudge. Le service du modèle et la survie de la machine
restent dans scripts/banc_jour2.sh.
"""
import json, ast, sys, time, urllib.request
sys.path.insert(0, "scripts")
from java_ordre import contexte_juge

MODE, SORTIE = sys.argv[1], sys.argv[2]
CAMPAGNE = "benchmarks/rag-campaign.jsonl"
URL, MODELE = "http://localhost:11434/api/chat", "qwen2.5-coder:32b"

# L'invite de banc_notation.py est elle-même reprise mot pour mot de RagContextJudge.
sys.argv = ["banc_notation", "x", "y"]  # ce module lit argv à l'import
ns = {}
exec(compile(open("scripts/banc_notation.py").read().split("items = json.load")[0],
             "banc_notation", "exec"), ns)
SYSTEME, CONVENTIONS, SENTINELLE, CRITERES = (ns["SYSTEME"], ns["CONVENTIONS"],
                                              ns["SENTINELLE"], ns["CRITERES"])
CONTROLES = ns["CONTROLES"]

AJOUT_NOTE = ("\n\nRends une note globale entière de 0 à 10 dans le champ `note`, où 10 "
              "signifie un contexte parfaitement pertinent et 0 un contexte inutile.")

SCHEMA_BINAIRE = {
    "type": "object", "additionalProperties": False,
    "required": ["checks", "verdict", "reason"],
    "properties": {
        "checks": {"type": "object", "additionalProperties": False, "required": CONTROLES,
                   "properties": {c: {"type": "boolean"} for c in CONTROLES}},
        "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
        "reason": {"type": "string"}}}
SCHEMA_NOTE = {
    "type": "object", "additionalProperties": False, "required": ["note", "reason"],
    "properties": {"note": {"type": "integer", "minimum": 0, "maximum": 10},
                   "reason": {"type": "string"}}}

# (plafond, critères dans l'invite, sortie attendue, schéma, num_ctx, champ lu au journal)
DISPOSITIFS = {
    "repro":   (6000, True,  SYSTEME,              SCHEMA_BINAIRE, 20480, "verdict"),
    "temoin":  (6000, True,  SYSTEME,              SCHEMA_BINAIRE, 20480, "verdict"),
    "plafond": (None, True,  SYSTEME,              SCHEMA_BINAIRE, 20480, "verdict"),
    "B":       (6000, False, SYSTEME + AJOUT_NOTE, SCHEMA_NOTE,    20480, "note"),
    "C":       (6000, True,  SYSTEME + AJOUT_NOTE, SCHEMA_NOTE,    20480, "note"),
}
PLAFOND, AVEC_CRITERES, TETE, SCHEMA, NUM_CTX, CHAMP = DISPOSITIFS[MODE]
SYSTEME_FINAL = TETE + "\n\n" + CONVENTIONS


def invite(question, texte):
    bloc = ("### CONTEXTE / RAG\n%s\n\n### ENTREE / REQUÊTE\n%s\n\n### SORTIE À ÉVALUER\n%s"
            % (texte, question, SENTINELLE))
    return bloc + ("\n\n### CRITÈRES DE VALIDATION\n" + CRITERES if AVEC_CRITERES else "")


def juge(user):
    corps = json.dumps({"model": MODELE, "stream": False, "format": SCHEMA,
                        "options": {"temperature": 0, "num_predict": 4096, "num_ctx": NUM_CTX},
                        "messages": [{"role": "system", "content": SYSTEME_FINAL},
                                     {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(URL, corps, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        rep = json.loads(r.read())
    return json.loads(rep["message"]["content"]), rep.get("prompt_eval_count")


def extraits(d):
    c = d["context"]
    return [x for x in (c if isinstance(c, list) else ast.literal_eval(c)) if isinstance(x, str)]


camp = [json.loads(l) for l in open(CAMPAGNE)]
if MODE == "repro":
    # Contrôle de reproduction : 12 contextes QUE LE PLAFOND NE TOUCHAIT PAS, 4 par bras,
    # les premiers par ordre alphabétique de question — règle fixée au pré-enregistrement.
    intacts = [d for d in camp if len("\n---\n".join(extraits(d))) <= 6000]
    camp = [d for a in ("vector", "vector-bm25", "graphrag")
            for d in sorted((x for x in intacts if x["arm"] == a), key=lambda x: x["question"])[:4]]

sortie, echecs = open(SORTIE, "w"), 0
for n, d in enumerate(camp, 1):
    texte = contexte_juge(d["question"], extraits(d), plafond=PLAFOND)
    t0 = time.time()
    try:
        v, jetons = juge(invite(d["question"], texte))
        err = None
    except Exception as e:
        v, jetons, err, echecs = None, None, str(e), echecs + 1
    sortie.write(json.dumps({"mode": MODE, "arm": d["arm"], "question": d["question"],
                             "caracteres": len(texte), "jetons_invite": jetons, "sortie": v,
                             "erreur": err, "secondes": round(time.time() - t0, 1)},
                            ensure_ascii=False) + "\n")
    sortie.flush()
    print(f"[{MODE}] [{n:3}/{len(camp)}] {d['arm']:11} {len(texte):6}car "
          f"{str(jetons or '?'):>6}jet -> {v[CHAMP] if v else 'ERREUR ' + err[:50]}", flush=True)
print(f"[{MODE}] TERMINÉ — {echecs} échecs sur {len(camp)}")
