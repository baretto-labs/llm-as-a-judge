"""Banc notation graduée vs verdict binaire — dispositif figé dans
benchmarks/PREENREGISTREMENT_NOTATION.md.

Python et non shell : mélanges graînés rejouables, assemblage de deux schémas JSON et
appariement des 120 jugements. Le service du modèle et la survie de la machine restent
dans scripts/banc_notation.sh.
"""
import json, random, sys, urllib.request, time, zlib

ITEMS, SORTIE = sys.argv[1], sys.argv[2]
URL = "http://localhost:11434/api/chat"
MODELE = "qwen2.5-coder:32b"
CONTROLES = ["contexte_pertinent", "contexte_suffisant", "bruit_maitrise"]

SYSTEME = ("Tu es un juge IA ultra-rigoureux. TÂCHE: RAG_CONTEXT_RELEVANCE. "
           "Analyse la situation pas à pas dans <thinking> avant de rendre ton verdict JSON.")
SENTINELLE = ("(la sortie évaluée est le contexte ci-dessus : ce sont les extraits que le moteur "
              "de recherche a retournés pour cette requête)")
CRITERES = """1. contexte_pertinent: Au moins un extrait du contexte porte directement sur les symboles ou notions visés par la requête.
2. contexte_suffisant: Les extraits fournis contiennent toutes les informations nécessaires pour répondre entièrement à la requête.
3. bruit_maitrise: Le contexte ne noie pas l'information utile sous des extraits hors sujet."""
CONVENTIONS = open("judge-finetune/configs/conventions.md").read()

def schema(final):
    props = {c: {"type": "boolean"} for c in CONTROLES}
    return {"type": "object", "additionalProperties": False,
            "required": ["checks", *final, "reason"],
            "properties": {
                "checks": {"type": "object", "additionalProperties": False,
                           "required": CONTROLES, "properties": props},
                **({"verdict": {"type": "string", "enum": ["PASS", "FAIL"]}} if final == ["verdict"]
                   else {"note": {"type": "integer", "minimum": 0, "maximum": 10}}),
                "reason": {"type": "string"}}}

FORMATS = {
    "binaire": (["verdict"], ""),
    "note": (["note"], "\n\nRends en plus une note globale entière de 0 à 10 dans le champ `note`, "
                       "où 10 signifie un contexte parfaitement pertinent et 0 un contexte inutile."),
}

def invite(question, chunks):
    return ("### CONTEXTE / RAG\n%s\n\n### ENTREE / REQUÊTE\n%s\n\n"
            "### SORTIE À ÉVALUER\n%s\n\n### CRITÈRES DE VALIDATION\n%s"
            % ("\n---\n".join(chunks), question, SENTINELLE, CRITERES))

def juge(systeme, user, sch):
    corps = json.dumps({"model": MODELE, "stream": False, "format": sch,
                        "options": {"temperature": 0, "num_predict": 4096},
                        "messages": [{"role": "system", "content": systeme},
                                     {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(URL, corps, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(json.loads(r.read())["message"]["content"])

items = json.load(open(ITEMS))
sortie = open(SORTIE, "w")
n = 0
for i, it in enumerate(items):
    base = it["chunks"]
    passes = [("temoin", 0, base), ("temoin", 1, base)]
    # zlib.crc32 et non hash() : hash() est graîné par processus, la permutation ne serait
    # pas rejouable. On exige aussi que chaque permutation diffère de l'ordre de base et des
    # précédentes, sans quoi une « permutation » identique diluerait la mesure.
    graine = zlib.crc32(it["question"].encode())
    vus, k = [base], 0
    while len(vus) < 4:
        c = list(base)
        random.Random(graine + k).shuffle(c); k += 1
        if c not in vus:
            vus.append(c)
    for p, c in enumerate(vus[1:]):
        passes.append(("permute", p, c))
    for fmt, (final, ajout) in FORMATS.items():
        sch = schema(final)
        for genre, p, chunks in passes:
            t0 = time.time()
            try:
                v = juge(SYSTEME + ajout + "\n\n" + CONVENTIONS, invite(it["question"], chunks), sch)
                err = None
            except Exception as e:
                v, err = None, str(e)
            n += 1
            rec = {"item": i, "arm": it["arm"], "question": it["question"], "format": fmt,
                   "genre": genre, "passe": p, "ordre": [base.index(c) for c in chunks],
                   "sortie": v, "erreur": err, "secondes": round(time.time() - t0, 1)}
            sortie.write(json.dumps(rec, ensure_ascii=False) + "\n"); sortie.flush()
            print(f"[{n:3}/120] item {i+1:2} {fmt:7} {genre:8} p{p} -> "
                  f"{(v or {}).get('verdict') or (v or {}).get('note') if v else 'ERREUR ' + err[:40]}",
                  flush=True)
print("JUGEMENTS TERMINÉS")
