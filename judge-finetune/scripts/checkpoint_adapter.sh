#!/usr/bin/env bash
# Assemble a servable adapter directory from a numbered mlx-lm checkpoint.
#
#   ./scripts/checkpoint_adapter.sh adapters/14b-judge 200 adapters/14b-judge-ckpt200
#
# Why this exists: `mlx_lm.server --adapter-path DIR` expects DIR to hold
# adapter_config.json and adapters.safetensors. Training writes numbered
# checkpoints beside the final weights, so serving a checkpoint other than the
# last one means building that layout explicitly.
#
# Why checkpoint 200: PREENREGISTREMENT.md, option C. Validation loss bottoms
# around iteration 250 then climbs, so the final adapter at 400 is the overfitted
# one. Serving adapters.safetensors without thinking would serve exactly that.
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="${1:?usage: checkpoint_adapter.sh <dossier-entrainement> <iteration> <dossier-cible>}"
ITER="${2:?iteration manquante (ex. 200)}"
DEST="${3:?dossier cible manquant}"

printf -v FICHIER "%07d_adapters.safetensors" "$ITER"

[ -d "$SRC" ] || { echo "dossier d'entraînement absent : $SRC" >&2; exit 1; }
[ -f "$SRC/adapter_config.json" ] || { echo "adapter_config.json absent de $SRC" >&2; exit 1; }
[ -f "$SRC/$FICHIER" ] || {
    echo "checkpoint $ITER absent de $SRC. Présents :" >&2
    ls "$SRC" | grep '_adapters.safetensors' >&2 || echo "  aucun" >&2
    exit 1
}

# Jamais d'écrasement silencieux : deux checkpoints mélangés dans un même dossier
# ne se distinguent plus, et c'est l'adaptateur servi au benchmark.
[ -e "$DEST" ] && { echo "$DEST existe déjà — le supprimer délibérément d'abord" >&2; exit 1; }

mkdir -p "$DEST"
cp "$SRC/adapter_config.json" "$DEST/adapter_config.json"
cp "$SRC/$FICHIER" "$DEST/adapters.safetensors"

# Trace de provenance : sans elle, un dossier d'adaptateur ne dit pas de quel
# run ni de quelle itération il sort, et le chiffre publié devient invérifiable.
cat > "$DEST/PROVENANCE.txt" <<EOF
source      : $SRC/$FICHIER
iteration   : $ITER
assemble le : $(date -Iseconds)
empreinte   : $(shasum -a 256 "$SRC/$FICHIER" | cut -d' ' -f1)
EOF

echo "$DEST prêt :"
ls -la "$DEST"
