"""Démo enregistrée du talk : une question, deux contextes (vectoriel, graphe), le juge en direct.

    python3 -I scripts/demo_juge.py ["question"]

Rejoue le dispositif « plafond » de banc_jour2.py (contextes entiers, critères dans l'invite,
verdict binaire, température 0) sur une seule question, pour que la démo montre exactement
le juge qui a produit les chiffres de la diapo « Premier verdict ».

Python et non shell : l'invite est assemblée en Python (banc_notation.py, java_ordre.py) et
doit être reprise mot pour mot.
"""
import json, ast, sys, time, urllib.request, threading
sys.path.insert(0, "scripts")
from java_ordre import contexte_juge, couverture

QUESTION = sys.argv[1] if len(sys.argv) > 1 else "What does DocumentIndexingPipeline implement?"
BRAS = [("vector", "VECTORIEL"), ("graphrag", "GRAPHE")]
CAMPAGNE = "benchmarks/rag-campaign.jsonl"
URL, MODELE = "http://localhost:11434/api/chat", "qwen2.5-coder:32b"

# Même extraction que banc_jour2.py : l'invite de banc_notation.py, reprise de RagContextJudge.
sys.argv = ["banc_notation", "x", "y"]
ns = {}
exec(compile(open("scripts/banc_notation.py").read().split("items = json.load")[0],
             "banc_notation", "exec"), ns)
SYSTEME, CONVENTIONS, SENTINELLE, CRITERES, CONTROLES = (
    ns["SYSTEME"], ns["CONVENTIONS"], ns["SENTINELLE"], ns["CRITERES"], ns["CONTROLES"])
SCHEMA = ns["schema"](["verdict"])

GRAS, ROUGE, VERT, GRIS, FIN = "\033[1m", "\033[31m", "\033[32m", "\033[90m", "\033[0m"


def invite(question, texte):
    return ("### CONTEXTE / RAG\n%s\n\n### ENTREE / REQUÊTE\n%s\n\n### SORTIE À ÉVALUER\n%s"
            "\n\n### CRITÈRES DE VALIDATION\n%s" % (texte, question, SENTINELLE, CRITERES))


def juge(user):
    corps = json.dumps({"model": MODELE, "stream": False, "format": SCHEMA,
                        "options": {"temperature": 0, "num_predict": 4096, "num_ctx": 20480},
                        "messages": [{"role": "system", "content": SYSTEME + "\n\n" + CONVENTIONS},
                                     {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(URL, corps, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        return json.loads(json.loads(r.read())["message"]["content"])


def attendre(fini):
    t0 = time.time()
    while not fini.wait(1):
        print(f"\r{GRIS}  le juge lit la copie… {int(time.time() - t0)} s{FIN}", end="", flush=True)
    print("\r" + " " * 40 + "\r", end="")


camp = {d["arm"]: d for d in map(json.loads, open(CAMPAGNE)) if d["question"] == QUESTION}
if not camp:
    sys.exit(f"question absente de {CAMPAGNE} : {QUESTION}")

print(f"\n{GRAS}QUESTION{FIN}  {QUESTION}\n")
for bras, titre in BRAS:
    d = camp[bras]
    c = d["context"]
    extraits = [x for x in (c if isinstance(c, list) else ast.literal_eval(c)) if isinstance(x, str)]
    texte = contexte_juge(QUESTION, extraits, plafond=None)

    print(f"{GRAS}━━━ {titre} ━━━{FIN}")
    print(f"{GRIS}extraits récupérés :{FIN}")
    for x in extraits:
        print(f"  · {x.strip().splitlines()[0][:100]}")
    trouves = [h for h in d["expected"] if h.lower() in texte.lower()]
    print(f"{GRIS}indices attendus :{FIN} " + "  ".join(
        f"{VERT}✓ {h}{FIN}" if h in trouves else f"{ROUGE}✗ {h}{FIN}" for h in d["expected"])
        + f"   {GRIS}hintCoverage = {couverture(texte, d['expected']):.2f}{FIN}")

    fini, res = threading.Event(), {}

    def appel():
        try:
            res["v"] = juge(invite(QUESTION, texte))
        except Exception as e:
            res["erreur"] = e
        finally:
            fini.set()

    threading.Thread(target=appel, daemon=True).start()
    attendre(fini)
    if "erreur" in res:
        sys.exit(f"{ROUGE}le juge n'a pas répondu : {res['erreur']}{FIN}")
    v = res["v"]
    for k in CONTROLES:
        print(f"  {VERT + '☑' if v['checks'][k] else ROUGE + '☒'} {k}{FIN}")
    couleur = VERT if v["verdict"] == "PASS" else ROUGE
    print(f"  {GRAS}{couleur}{v['verdict']}{FIN}  {v['reason']}\n")
