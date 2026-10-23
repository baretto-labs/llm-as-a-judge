#!/usr/bin/env zsh
# Enchaîne les bancs du 2026-10-20 : contrôle de reproduction, plafond, puis notes B et C.
# Dispositifs figés dans benchmarks/PREENREGISTREMENT_PLAFOND.md et
# benchmarks/PREENREGISTREMENT_NOTE_BC.md — ce script ne décide de rien, il exécute.
#
#   ./scripts/banc_jour2.sh
#
# Le Mac ne dort pas tant que ce script vit (caffeinate adossé à son PID).
set -euo pipefail
cd "${0:A:h}/.."

SORTIES=(benchmarks/plafond/repro.jsonl benchmarks/plafond/temoin.jsonl
         benchmarks/plafond/sans-plafond.jsonl benchmarks/notation/bras-B.jsonl
         benchmarks/notation/bras-C.jsonl)
for f in $SORTIES; do
    [[ -e $f ]] && { print -u2 "$f existe deja : ce banc a deja tourne."; exit 1; }
done
mkdir -p benchmarks/plafond benchmarks/notation

# Preuve positive avant de depenser 540 jugements : Ollama repond, le modele est la.
curl -sf http://localhost:11434/api/tags >/dev/null \
    || { print -u2 "Ollama ne repond pas sur 11434"; exit 1; }
ollama list | awk 'NR>1 {print $1}' | grep -qx qwen2.5-coder:32b \
    || { print -u2 "modele absent d'Ollama : qwen2.5-coder:32b"; exit 1; }
print "[jour2] Ollama repond, qwen2.5-coder:32b present"

caffeinate -i -w $$ &
print "[jour2] veille inhibee (caffeinate adosse au PID $$)"

print "\n===== 1/4 CONTROLE DE REPRODUCTION (12 contextes intacts, num_ctx=20480) ====="
python3 -I scripts/banc_jour2.py repro benchmarks/plafond/repro.jsonl

REJOUER=0
python3 -I scripts/controle_repro.py benchmarks/plafond/repro.jsonl || REJOUER=1

if (( REJOUER )); then
    print "\n===== 1bis/4 TEMOIN AVEC PLAFOND rejoue en entier (180) ====="
    python3 -I scripts/banc_jour2.py temoin benchmarks/plafond/temoin.jsonl
else
    print "\n[jour2] temoin non rejoue : le bras A en banque sert de cote « avec plafond »."
fi

print "\n===== 2/4 BANC PLAFOND — 180 contextes SANS troncature ====="
python3 -I scripts/banc_jour2.py plafond benchmarks/plafond/sans-plafond.jsonl

print "\n===== 3/4 BRAS B — note seule, SANS criteres (180) ====="
python3 -I scripts/banc_jour2.py B benchmarks/notation/bras-B.jsonl

print "\n===== 4/4 BRAS C — note seule, AVEC criteres (180) ====="
python3 -I scripts/banc_jour2.py C benchmarks/notation/bras-C.jsonl

print "\n[jour2] TOUT EST TERMINE a $(date +%H:%M)"
