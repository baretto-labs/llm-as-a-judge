#!/usr/bin/env bash
# Juge la campagne avec un modèle servi par Ollama, en SORTIE STRUCTURÉE.
#
#   ./scripts/juge_campagne_ollama.sh schema-coder32b qwen2.5-coder:32b
#
# Pourquoi un script distinct de juge_campagne.sh : celui-là démarre mlx_lm.server, qui
# IGNORE response_format en silence (0.31.3, aucune occurrence dans server.py). Un run
# « contraint » servi par MLX ne le serait pas, et rien ne le dirait. Ollama sert ici.
#
# Env : CAMPAGNE, SUFFIXE
set -euo pipefail
cd "$(dirname "$0")/.."

ETIQUETTE="${1:?usage: juge_campagne_ollama.sh <étiquette> <modèle ollama> [args maven...]}"
MODELE="${2:?usage: juge_campagne_ollama.sh <étiquette> <modèle ollama> [args maven...]}"
shift 2
CAMPAGNE="${CAMPAGNE:-benchmarks/rag-campaign.jsonl}"
SUFFIXE="${SUFFIXE:-judge-finetune/configs/conventions.md}"
SORTIE="${CAMPAGNE%.jsonl}-juge-$ETIQUETTE.jsonl"

[ -f "$CAMPAGNE" ] || { echo "campagne absente : $CAMPAGNE"; exit 1; }
[ -e "$SORTIE" ] && { echo "$SORTIE existe déjà : cette étiquette a déjà jugé cette campagne."; exit 1; }
[ -f "$SUFFIXE" ] || { echo "conventions absentes : $SUFFIXE"; exit 1; }

# Preuve positive que le modèle est servi, avant de dépenser 360 jugements.
ollama list | awk 'NR>1 {print $1}' | grep -qx "$MODELE" \
    || { echo "modèle absent d'Ollama : $MODELE (ollama pull $MODELE)"; exit 1; }
curl -sf http://localhost:11434/api/tags >/dev/null \
    || { echo "Ollama ne répond pas sur 11434"; exit 1; }
echo "[$ETIQUETTE] Ollama répond, modèle $MODELE présent"

mvn test -Dtest=RagCampaignJudge -DfailIfNoTests=false \
    -Drag.campaign.file="$CAMPAGNE" \
    -Drag.campaign.judge.label="$ETIQUETTE" \
    -Djmh.judge.provider=ollama       -Djmh.judge.url="http://localhost:11434" \
    -Djmh.judge.model="$MODELE"       -Djmh.judge.suffix="$SUFFIXE" \
    -Djmh.judge.schema=true           -Djmh.judge.adapter= \
    -Djmh.answerjudge.provider=ollama -Djmh.answerjudge.url="http://localhost:11434" \
    -Djmh.answerjudge.model="$MODELE" -Djmh.answerjudge.suffix="$SUFFIXE" \
    -Djmh.answerjudge.schema=true \
    "$@"

echo "[$ETIQUETTE] écrit : $SORTIE"
