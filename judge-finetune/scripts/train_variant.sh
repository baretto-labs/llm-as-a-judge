#!/usr/bin/env bash
# Trains one judge variant and measures what it cost, which is a published claim of
# this study and cannot be recovered afterwards.
#
#   MODEL=... ADAPTER=... ./scripts/train_variant.sh 14b --train --fine-tune-type lora ...
#   make train-14b
#
# Weights are fetched BEFORE the timed region: the 32B is ~18 GB and a download folded
# into the training time would misstate the headline figure of the report.
#
# Writes mesures/cout/train-<name>.json — see PREENREGISTREMENT.md §8. Deliberately NOT
# under results/, which is git-ignored and wiped by `make clean-results`: these figures
# cannot be recovered without re-running the training they measure.
# Env: MODEL, ADAPTER, VENV, OUT
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="${1:?usage: MODEL=... ADAPTER=... train_variant.sh <name> [lora args...]}"
shift
MODEL="${MODEL:?MODEL manquant (ex. mlx-community/Qwen2.5-Coder-14B-Instruct-4bit)}"
ADAPTER="${ADAPTER:?ADAPTER manquant (ex. adapters/14b-judge)}"
VENV="${VENV:-.venv}"
OUT="${OUT:-mesures/cout}"
PY="$VENV/bin/python"
LORA="$VENV/bin/mlx_lm.lora"

[ -x "$PY" ]   || { echo "venv absent : lance 'make setup'"; exit 1; }
[ -x "$LORA" ] || { echo "mlx_lm.lora absent : lance 'make setup'"; exit 1; }
[ -f data/mlx/train.jsonl ] || { echo "data/mlx/train.jsonl absent : lance 'make split'"; exit 1; }

mkdir -p "$OUT"
REPORT="$OUT/train-$NAME.json"
LOG="$OUT/train-$NAME.log"
TIMELOG="$(mktemp -t mlx-time-XXXX)"
trap 'rm -f "$TIMELOG"' EXIT

# ── Poids : récupérés hors chronomètre, et le temps de téléchargement est relevé à part.
echo "[$NAME] vérification du cache des poids ($MODEL)"
FETCH_START=$SECONDS
CACHED_BEFORE="$("$PY" - "$MODEL" <<'PYEOF'
import sys
from huggingface_hub import snapshot_download
try:
    snapshot_download(sys.argv[1], local_files_only=True)
    print("true")
except Exception:
    print("false")
PYEOF
)"
if [ "$CACHED_BEFORE" = "false" ]; then
    echo "[$NAME] poids absents du cache — téléchargement (hors mesure d'entraînement)"
    "$PY" -c "from huggingface_hub import snapshot_download; snapshot_download('$MODEL')"
fi
FETCH_S=$((SECONDS - FETCH_START))
echo "[$NAME] poids prêts (déjà en cache : $CACHED_BEFORE, ${FETCH_S}s)"

# ── Jetons réellement vus : mesurés sur les données, pas estimés.
echo "[$NAME] comptage des jetons du jeu d'entraînement"
TOKENS_JSON="$("$PY" - "$MODEL" <<'PYEOF'
import json, sys, statistics
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained(sys.argv[1])
out = {}
for nom in ("train", "valid"):
    longueurs = []
    with open(f"data/mlx/{nom}.jsonl") as f:
        for ligne in f:
            ex = json.loads(ligne)
            texte = "".join(m["content"] for m in ex["messages"])
            longueurs.append(len(tok(texte)["input_ids"]))
    longueurs.sort()
    out[nom] = {
        "exemples": len(longueurs),
        "jetons_total": sum(longueurs),
        "jetons_p50": statistics.median(longueurs),
        "jetons_p90": longueurs[int(0.9 * len(longueurs))],
        "jetons_max": max(longueurs),
    }
print(json.dumps(out))
PYEOF
)"
echo "[$NAME] $(echo "$TOKENS_JSON" | "$PY" -c "import json,sys; d=json.load(sys.stdin); print(f\"train {d['train']['jetons_total']} jetons (p50 {d['train']['jetons_p50']}, max {d['train']['jetons_max']})\")")"

# ── Entraînement, seule zone chronométrée.
DEBUT_ISO="$(date -Iseconds)"
echo "[$NAME] entraînement — journal : $LOG"
set +e
/usr/bin/time -l "$LORA" --model "$MODEL" --data data/mlx --adapter-path "$ADAPTER" "$@" \
    >"$LOG" 2>"$TIMELOG"
CODE=$?
set -e
FIN_ISO="$(date -Iseconds)"
cat "$TIMELOG" >>"$LOG"

if [ "$CODE" -ne 0 ]; then
    echo "[$NAME] échec de l'entraînement (code $CODE) :"
    tail -25 "$LOG"
    exit "$CODE"
fi

REAL_S="$(awk '/ real /{print $1; exit}' "$TIMELOG")"
MAX_RSS="$(awk '/maximum resident set size/{print $1; exit}' "$TIMELOG")"
PEAK_FOOT="$(awk '/peak memory footprint/{print $1; exit}' "$TIMELOG")"

# ── Relevé. Les versions et la machine sont épinglées : sans elles le chiffre n'est pas reproductible.
"$PY" - "$REPORT" "$NAME" "$MODEL" "$ADAPTER" "$DEBUT_ISO" "$FIN_ISO" \
       "$REAL_S" "$MAX_RSS" "$PEAK_FOOT" "$FETCH_S" "$CACHED_BEFORE" "$TOKENS_JSON" "$@" <<'PYEOF'
import json, platform, subprocess, sys
from importlib.metadata import version

(rapport, nom, modele, adapter, debut, fin,
 real_s, max_rss, peak_foot, fetch_s, cache_avant, tokens_json, *lora_args) = sys.argv[1:]

def sysctl(cle):
    try:
        return subprocess.run(["sysctl", "-n", cle], capture_output=True, text=True).stdout.strip()
    except Exception:
        return None

go = lambda octets: round(int(octets) / 1024**3, 2)
tokens = json.loads(tokens_json)

# Les arguments LoRA mêlent paires clé/valeur et drapeaux seuls (--train, --mask-prompt) :
# un simple zip par deux les décalerait et perdrait --iters.
args, i = {}, 0
while i < len(lora_args):
    cle = lora_args[i]
    if cle.startswith("--") and i + 1 < len(lora_args) and not lora_args[i + 1].startswith("--"):
        args[cle], i = lora_args[i + 1], i + 2
    else:
        args[cle], i = True, i + 1

# Jetons réellement vus = jetons par exemple x itérations x batch, le tirage étant avec remise.
iters = int(args.get("--iters", 0) or 0)
batch = int(args.get("--batch-size", 1) or 1)
moyenne = tokens["train"]["jetons_total"] / max(tokens["train"]["exemples"], 1)

releve = {
    "variante": nom,
    "modele": modele,
    "adapter": adapter,
    "debut": debut,
    "fin": fin,
    "entrainement": {
        "duree_s": float(real_s),
        "duree_lisible": f"{int(float(real_s)) // 60} min {int(float(real_s)) % 60} s",
        "memoire_pic_go": go(peak_foot),
        "memoire_rss_max_go": go(max_rss),
        "note_memoire": ("le chiffre à retenir est `memoire_pic_go` (peak memory footprint). Sur Apple "
                         "Silicon, les allocations Metal n'apparaissent pas dans le RSS, si bien que "
                         "`memoire_rss_max_go` est très inférieur et ne mesure pas l'empreinte réelle "
                         "de l'entraînement"),
        "iterations": iters,
        "batch_size": batch,
        "s_par_iteration": round(float(real_s) / iters, 2) if iters else None,
        "jetons_vus_estimes": int(moyenne * iters * batch) if iters else None,
    },
    "poids": {
        "integralement_en_cache_avant": cache_avant == "true",
        "duree_recuperation_s": int(fetch_s),
        "note": ("récupération hors chronomètre d'entraînement : un téléchargement inclus fausserait la "
                 "durée publiée. « intégralement en cache » signifie que TOUS les fichiers du dépôt "
                 "étaient présents — un cache partiel (fréquent, mlx-lm ne récupérant que ce qu'il lui "
                 "faut) compte comme faux et déclenche une complétion, mesurée ici et non dans la durée "
                 "d'entraînement"),
    },
    "donnees": tokens,
    "hyperparametres": args,
    "versions": {p: version(p) for p in ("mlx", "mlx-lm", "mlx-metal", "transformers")},
    "machine": {
        "processeur": sysctl("machdep.cpu.brand_string"),
        "coeurs": sysctl("hw.ncpu"),
        "memoire_go": go(sysctl("hw.memsize") or 0),
        "systeme": f"macOS {platform.mac_ver()[0]}",
    },
}
with open(rapport, "w") as f:
    json.dump(releve, f, ensure_ascii=False, indent=2)

e = releve["entrainement"]
print(f"\n[{nom}] === coût mesuré ===")
print(f"  durée            : {e['duree_lisible']}  ({e['s_par_iteration']} s/itération)")
print(f"  mémoire de pointe: {e['memoire_pic_go']} Go   (RSS max {e['memoire_rss_max_go']} Go)")
print(f"  jetons vus       : {e['jetons_vus_estimes']}")
print(f"  machine          : {releve['machine']['processeur']}, {releve['machine']['memoire_go']} Go")
print(f"  relevé           : {rapport}")
PYEOF
