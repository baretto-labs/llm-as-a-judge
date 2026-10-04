"""Le <thinking> pilote-t-il la décision du juge ?

Protocole figé dans fidelite/PREENREGISTREMENT.md, écrit avant cette exécution.

On impose au modèle le début de sa réponse — le bloc <thinking> — puis on le
laisse produire la suite. Bras A : son propre raisonnement. Bras B : celui d'un
autre item, de verdict de référence opposé. Si la décision ne bouge pas entre les
deux, le raisonnement affiché ne la pilote pas.

Génération gloutonne : on teste un mécanisme causal, pas une répétabilité.
"""
import json, re, sys, time
from pathlib import Path
from mlx_lm import load, generate

RACINE = Path(__file__).resolve().parent.parent
MODELE = "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit"
ADAPTATEUR = str(RACINE / "adapters" / "14b-judge-ckpt200")
GOLDEN = RACINE / "data" / "golden" / "test.jsonl"
PASSE1 = RACINE / "results" / "runs" / "14B-finetuned.jsonl"
SORTIE = Path(__file__).resolve().parent / "resultats" / "generations.jsonl"

LABELS = {"PASS", "FAIL"}


def verdict(texte):
    """Dernier objet JSON du texte qui porte un verdict. None si absent."""
    dec = json.JSONDecoder()
    i = texte.rfind("{")
    while i >= 0:
        try:
            o, _ = dec.raw_decode(texte[i:])
            if isinstance(o, dict) and o.get("verdict") in LABELS:
                return o
        except json.JSONDecodeError:
            pass
        i = texte.rfind("{", 0, i)
    return None


def bloc_thinking(texte):
    m = re.search(r"<thinking>.*?</thinking>", texte, re.S)
    return m.group(0) if m else None


def charger():
    """Items de l'étalon, avec le raisonnement que le juge avait écrit en passe 1."""
    gold = {}
    for ligne in GOLDEN.open(encoding="utf-8"):
        d = json.loads(ligne)
        o = verdict(d["messages"][-1]["content"])
        gold[d["meta"]["id"]] = {
            "invite": [m for m in d["messages"] if m["role"] != "assistant"],
            "reference": o["verdict"],
        }
    manquants = []
    for ligne in PASSE1.open(encoding="utf-8"):
        d = json.loads(ligne)
        if d["pass"] != 1 or d["id"] not in gold:
            continue
        t = bloc_thinking(d.get("text") or "")
        if t is None:
            manquants.append(d["id"])
            continue
        gold[d["id"]]["thinking"] = t
        gold[d["id"]]["verdict_origine"] = (verdict(d["text"]) or {}).get("verdict")
    items = {k: v for k, v in gold.items() if "thinking" in v}
    if manquants:
        print(f"  [!] {len(manquants)} items sans bloc <thinking> en passe 1, écartés")
    return items


def apparier(items):
    """PASS de rang n reçoit le raisonnement du FAIL de rang n, et l'inverse.

    Déterministe : tri par identifiant, aucune part de hasard, rejouable à
    l'identique. Les items en surnombre d'un côté sont écartés plutôt que
    appariés à un verdict identique — l'appariement DOIT opposer les verdicts.
    """
    p = sorted(k for k, v in items.items() if v["reference"] == "PASS")
    f = sorted(k for k, v in items.items() if v["reference"] == "FAIL")
    paires = {}
    for a, b in zip(p, f):
        paires[a], paires[b] = b, a
    ecartes = set(p[len(f):]) | set(f[len(p):])
    return paires, ecartes


def main():
    items = charger()
    paires, ecartes = apparier(items)
    print(f"  {len(items)} items exploitables, {len(paires)} appariés, {len(ecartes)} écartés")

    print(f"  chargement du modèle + adaptateur…")
    modele, tok = load(MODELE, adapter_path=ADAPTATEUR)

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    deja = set()
    if SORTIE.exists():
        for l in SORTIE.open(encoding="utf-8"):
            d = json.loads(l)
            deja.add((d["bras"], d["id"]))
        print(f"  {len(deja)} générations déjà en cache")

    taches = [(bras, i) for i in sorted(paires) for bras in ("A", "B")
              if (bras, i) not in deja]
    print(f"  {len(taches)} générations à produire\n")

    with SORTIE.open("a", encoding="utf-8") as sortie:
        for n, (bras, ident) in enumerate(taches, 1):
            it = items[ident]
            source = ident if bras == "A" else paires[ident]
            impose = items[source]["thinking"]
            invite = tok.apply_chat_template(it["invite"], add_generation_prompt=True,
                                             tokenize=False)
            t0 = time.perf_counter()
            suite = generate(modele, tok, prompt=invite + impose + "\n",
                             max_tokens=400, verbose=False)
            dt = time.perf_counter() - t0
            o = verdict(suite)
            sortie.write(json.dumps({
                "bras": bras, "id": ident, "thinking_de": source,
                "reference": it["reference"],
                "verdict_origine": it.get("verdict_origine"),
                "verdict": (o or {}).get("verdict"),
                "checks": (o or {}).get("checks"),
                "suite": suite, "duree_s": round(dt, 1),
            }, ensure_ascii=False) + "\n")
            sortie.flush()
            print(f"  {n}/{len(taches)}  bras {bras}  {ident}  "
                  f"→ {(o or {}).get('verdict') or 'INVALIDE'}  {dt:.0f}s", flush=True)


if __name__ == "__main__":
    main()
