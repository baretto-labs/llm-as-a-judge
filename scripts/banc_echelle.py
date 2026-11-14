"""Note 0-10 sur les 180 contextes de la campagne — dispositif figé dans
benchmarks/PREENREGISTREMENT_ECHELLE.md. Réutilise l'invite de scripts/banc_notation.py,
qui reprend mot pour mot celle de RagContextJudge."""
import json, ast, sys, time, importlib.util
sys.path.insert(0, "scripts")
from java_ordre import contexte_juge

spec = importlib.util.spec_from_file_location("bn", "scripts/banc_notation.py")
# banc_notation.py exécute son banc à l'import ; on ne reprend donc que son texte.
src = open("scripts/banc_notation.py").read()
ns = {}
exec(compile(src.split("items = json.load")[0], "banc_notation", "exec"), ns)
juge, invite, schema = ns["juge"], ns["invite"], ns["schema"]
SYSTEME, CONVENTIONS, FORMATS = ns["SYSTEME"], ns["CONVENTIONS"], ns["FORMATS"]

final, ajout = FORMATS["note"]
sch = schema(final)
systeme = SYSTEME + ajout + "\n\n" + CONVENTIONS

camp = [json.loads(l) for l in open(sys.argv[1])]
sortie = open(sys.argv[2], "w")
echecs = 0
for n, d in enumerate(camp, 1):
    c = d["context"]
    chunks = [x for x in (c if isinstance(c, list) else ast.literal_eval(c)) if isinstance(x, str)]
    # Ordre et troncature RÉPLIQUÉS de RagContextJudge (hashCode -> java.util.Random ->
    # Collections.shuffle -> troncature 6000). Vérifié le 2026-10-19 : hintCoverage recalculé
    # identique aux 180 valeurs stockées. Sans ça, les items tronqués ne verraient pas le même
    # contenu que le verdict binaire auquel la question 2 les compare.
    texte = contexte_juge(d["question"], chunks)
    t0 = time.time()
    try:
        v, err = juge(systeme, invite(d["question"], [texte]), sch), None
    except Exception as e:
        v, err, echecs = None, str(e), echecs + 1
    sortie.write(json.dumps({"arm": d["arm"], "question": d["question"], "sortie": v,
                             "erreur": err, "secondes": round(time.time() - t0, 1)},
                            ensure_ascii=False) + "\n")
    sortie.flush()
    print(f"[{n:3}/{len(camp)}] {d['arm']:11} -> {v['note'] if v else 'ERREUR ' + err[:40]}", flush=True)
print(f"JUGEMENTS TERMINÉS — {echecs} échecs")
