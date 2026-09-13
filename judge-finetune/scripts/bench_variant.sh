#!/usr/bin/env bash
# Benchmarks one judge variant locally: starts mlx_lm.server, waits for it, runs the
# benchmark on that variant only, then stops the server.
#
#   ./scripts/bench_variant.sh 14B-baseline
#   ./scripts/bench_variant.sh 14B-finetuned --passes 1        # extra args go to the benchmark
#
# Env: CONFIG, GOLDEN, OUT, VENV, WAIT_S (server startup budget, first run downloads the model)
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="${1:?usage: bench_variant.sh <variant-name> [benchmark args...]}"
shift
CONFIG="${CONFIG:-configs/variants.json}"
GOLDEN="${GOLDEN:-data/golden/test.jsonl}"
OUT="${OUT:-results}"
VENV="${VENV:-.venv}"
WAIT_S="${WAIT_S:-1800}"
PY="$VENV/bin/python"

[ -x "$PY" ] || { echo "venv absent : lance 'make setup'"; exit 1; }
[ -f "$CONFIG" ] || { echo "config absente : cp configs/variants.example.json $CONFIG"; exit 1; }
[ -f "$GOLDEN" ] || { echo "golden set absent : lance 'make split'"; exit 1; }

# Read serving parameters for this variant out of the shared config.
read -r MODEL ADAPTER PORT <<EOF
$("$PY" - "$CONFIG" "$NAME" <<'PYEOF'
import json, sys, urllib.parse
config, name = sys.argv[1], sys.argv[2]
variants = json.load(open(config))["variants"]
try:
    v = next(v for v in variants if v["name"] == name)
except StopIteration:
    sys.exit(f"variante inconnue: {name} (disponibles: {', '.join(x['name'] for x in variants)})")
port = urllib.parse.urlparse(v["base_url"]).port or 8080
print(v.get("serve_model") or v["model"], v.get("serve_adapter") or "-", port)
PYEOF
)
EOF

SERVER_ARGS=(--model "$MODEL" --port "$PORT" --log-level WARNING)
[ "$ADAPTER" != "-" ] && SERVER_ARGS+=(--adapter-path "$ADAPTER")

LOG="$(mktemp -t mlx-server-XXXX).log"
echo "[$NAME] démarrage de mlx_lm.server sur le port $PORT (modèle $MODEL, adapter $ADAPTER)"
echo "[$NAME] log serveur : $LOG"
"$VENV/bin/mlx_lm.server" "${SERVER_ARGS[@]}" >"$LOG" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true; wait "$SERVER_PID" 2>/dev/null || true' EXIT

# First run downloads the weights, so the wait budget is generous.
deadline=$((SECONDS + WAIT_S))
until curl -sf "http://127.0.0.1:$PORT/v1/models" >/dev/null 2>&1; do
    kill -0 "$SERVER_PID" 2>/dev/null || { echo "[$NAME] le serveur s'est arrêté :"; tail -20 "$LOG"; exit 1; }
    [ "$SECONDS" -lt "$deadline" ] || { echo "[$NAME] serveur non prêt après ${WAIT_S}s :"; tail -20 "$LOG"; exit 1; }
    sleep 3
done
echo "[$NAME] serveur prêt, lancement du benchmark"

"$PY" scripts/benchmark_judges.py --config "$CONFIG" --golden "$GOLDEN" --out "$OUT" --variants "$NAME" "$@"
