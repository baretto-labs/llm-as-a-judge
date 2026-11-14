#!/usr/bin/env bash
# Fait juger une campagne RAG par UN juge servi localement par mlx_lm.server :
# démarre le serveur, attend qu'il réponde, lance RagCampaignJudge, arrête le serveur.
#
#   ./scripts/juge_campagne.sh 32B-conventions  mlx-community/Qwen2.5-Coder-32B-Instruct-4bit
#   ./scripts/juge_campagne.sh gemma-4-26b-a4b  mlx-community/gemma-4-26b-a4b-it-4bit
#
# Un seul serveur à la fois : les deux juges pèsent 17 et 14 Go, ils ne cohabitent pas.
# Le générateur Ollama doit être déchargé avant (`ollama stop qwen3.8:27b`), sans quoi
# 18 Go de générateur plus le juge dépassent la limite wired de ~27 Go.
#
# Env : CAMPAGNE (fichier de générations), PORT, VENV, WAIT_S, SUFFIXE (conventions),
#       MAX_TOKENS (budget de génération du serveur ; défaut mlx_lm.server = 512)
#
# MAX_TOKENS existe depuis le 2026-10-19. Le défaut de 512 a mis gemma-4-26b-a4b en panne
# muette : ce modèle raisonne dans le champ `reasoning` d'OpenAI, épuise les 512 jetons et
# ne rend JAMAIS de `content` — 326 INVALID sur 338 jugements, zéro message d'erreur, le
# serveur répondant 200. Sonde du 2026-10-19 : à 80 jetons content=None finish=length ;
# à 3000 jetons, {"verdict":"PASS"} rendu en 112 jetons.
set -euo pipefail
cd "$(dirname "$0")/.."

ETIQUETTE="${1:?usage: juge_campagne.sh <étiquette> <modèle mlx> [args maven...]}"
MODELE="${2:?usage: juge_campagne.sh <étiquette> <modèle mlx> [args maven...]}"
shift 2

CAMPAGNE="${CAMPAGNE:-benchmarks/rag-campaign.jsonl}"
PORT="${PORT:-8090}"
VENV="${VENV:-judge-finetune/.venv}"
WAIT_S="${WAIT_S:-1800}"
SUFFIXE="${SUFFIXE:-judge-finetune/configs/conventions.md}"

[ -x "$VENV/bin/mlx_lm.server" ] || { echo "venv absent : cd judge-finetune && make setup"; exit 1; }
[ -f "$CAMPAGNE" ] || { echo "campagne absente : $CAMPAGNE — lance RagCampaignGenerate"; exit 1; }
[ -f "$SUFFIXE" ]  || { echo "conventions absentes : $SUFFIXE"; exit 1; }

SORTIE="${CAMPAGNE%.jsonl}-juge-$ETIQUETTE.jsonl"
[ -e "$SORTIE" ] && { echo "$SORTIE existe déjà : cette étiquette a déjà jugé cette campagne."; exit 1; }

# Garde-fou mémoire, et non un rappel dans un commentaire : un « [METAL] Insufficient Memory »
# a déjà tué un banc à 22 items le 2026-10-17. `ollama ps` ne liste que les modèles RÉSIDENTS.
if RESIDENTS="$(ollama ps 2>/dev/null | tail -n +2)" && [ -n "$RESIDENTS" ]; then
    echo "Un modèle Ollama est résident — il prendrait sa place en plus du juge :"
    echo "$RESIDENTS"
    echo "Décharge-le (\`ollama stop <modèle>\`), ou relance avec FORCE=1 si tu sais que ça tient."
    [ "${FORCE:-0}" = "1" ] || exit 1
fi

LOG="$(mktemp -t mlx-juge-XXXX).log"
echo "[$ETIQUETTE] mlx_lm.server port $PORT, modèle $MODELE"
echo "[$ETIQUETTE] log serveur : $LOG"
# --prompt-cache-size 1 : le préfixe n'est pas réutilisé d'un item à l'autre, retenir
# dix caches ne coûte que de la mémoire (voir judge-finetune/scripts/bench_variant.sh).
SERVEUR_ARGS=(--model "$MODELE" --port "$PORT" --log-level WARNING --prompt-cache-size 1)
[ -n "${MAX_TOKENS:-}" ] && SERVEUR_ARGS+=(--max-tokens "$MAX_TOKENS")
"$VENV/bin/mlx_lm.server" "${SERVEUR_ARGS[@]}" >"$LOG" 2>&1 &
SERVEUR=$!
trap 'kill "$SERVEUR" 2>/dev/null || true; wait "$SERVEUR" 2>/dev/null || true' EXIT

deadline=$((SECONDS + WAIT_S))
until curl -sf "http://127.0.0.1:$PORT/v1/models" >/dev/null 2>&1; do
    kill -0 "$SERVEUR" 2>/dev/null || { echo "[$ETIQUETTE] le serveur s'est arrêté :"; tail -20 "$LOG"; exit 1; }
    [ "$SECONDS" -lt "$deadline" ] || { echo "[$ETIQUETTE] serveur non prêt après ${WAIT_S}s :"; tail -20 "$LOG"; exit 1; }
    sleep 3
done
echo "[$ETIQUETTE] serveur prêt, lancement des jugements"

mvn test -Dtest=RagCampaignJudge -DfailIfNoTests=false \
    -Drag.campaign.file="$CAMPAGNE" \
    -Drag.campaign.judge.label="$ETIQUETTE" \
    -Djmh.judge.provider=openai      -Djmh.judge.url="http://127.0.0.1:$PORT/v1" \
    -Djmh.judge.model="$MODELE"      -Djmh.judge.suffix="$SUFFIXE" \
    -Djmh.answerjudge.provider=openai -Djmh.answerjudge.url="http://127.0.0.1:$PORT/v1" \
    -Djmh.answerjudge.model="$MODELE" -Djmh.answerjudge.suffix="$SUFFIXE" \
    "$@"

echo "[$ETIQUETTE] écrit : $SORTIE"
