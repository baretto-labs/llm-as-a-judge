#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run-benchmarks.sh  —  Lance les benchmarks RAG avec tous les scénarios
#
# Usage :
#   ./run-benchmarks.sh                  # mode rapide : 10 et 100 fichiers
#   ./run-benchmarks.sh --full           # mode complet : 10, 100, 1000, 10000
#   ./run-benchmarks.sh --indexation     # inclut aussi le benchmark d'indexation
#   ./run-benchmarks.sh --no-judge       # désactive le juge LLM (pas besoin du modèle 14B)
#   ./run-benchmarks.sh --scenario "hybrid|hybrid-graph"  # un seul scénario
#   ./run-benchmarks.sh --filecount "10,100"              # tailles custom
#   ./run-benchmarks.sh --source-dir /path/to/src         # mode réel (codebase existante)
#
# Mode réel (--source-dir) :
#   Indexe et interroge une vraie codebase Java au lieu de sources synthétiques.
#   Le paramètre fileCount est ignoré (1 seule taille : la codebase elle-même).
#   Exemple : ./run-benchmarks.sh --source-dir /Users/mehdi/Workspaces/Labs/OllamAssist/src/main/java \
#                                 --scenario "knn-only|hybrid,hybrid|hybrid,hybrid|hybrid-graph"
#
# Résultats sauvegardés dans :  target/benchmark-results/YYYY-MM-DD_HH-MM/
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Couleurs ──────────────────────────────────────────────────────────────────
BOLD='\033[1m'; CYAN='\033[0;36m'; GREEN='\033[0;32m'
YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'

log()  { echo -e "${CYAN}▶${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
die()  { echo -e "${RED}✗${NC} $*" >&2; exit 1; }
sep()  { echo -e "${CYAN}────────────────────────────────────────────────────${NC}"; }

# ── Defaults ──────────────────────────────────────────────────────────────────
ALL_SCENARIOS="knn-only|hybrid,hybrid|hybrid,hybrid|hybrid-graph,hybrid|hybrid-graph-hyde"
FILE_COUNTS_QUICK="10,100"
FILE_COUNTS_FULL="10,100,1000,10000"

FULL=false
WITH_INDEXATION=false
JUDGE_ENABLED=true
CUSTOM_SCENARIO=""
CUSTOM_FILE_COUNTS=""
SOURCE_DIR=""

# ── Parse arguments ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    --full)           FULL=true ;;
    --indexation)     WITH_INDEXATION=true ;;
    --no-judge)       JUDGE_ENABLED=false ;;
    --scenario)       CUSTOM_SCENARIO="$2"; shift ;;
    --filecount)      CUSTOM_FILE_COUNTS="$2"; shift ;;
    --source-dir)     SOURCE_DIR="$2"; shift ;;
    -h|--help)
      sed -n '2,18p' "$0" | sed 's/^# \?//'
      exit 0 ;;
    *) die "Option inconnue : $1  (--help pour l'aide)" ;;
  esac
  shift
done

# ── Résoudre les paramètres finaux ────────────────────────────────────────────
SCENARIOS=${CUSTOM_SCENARIO:-$ALL_SCENARIOS}

# Mode réel : --source-dir écrase fileCount et fixe le scénario par défaut (sans HyDE)
if [[ -n "$SOURCE_DIR" ]]; then
  [[ -d "$SOURCE_DIR" ]] || die "Le répertoire source n'existe pas : $SOURCE_DIR"
  FILE_COUNTS="1"
  [[ -z "$CUSTOM_SCENARIO" ]] && SCENARIOS="knn-only|hybrid,hybrid|hybrid,hybrid|hybrid-graph"
  # Export comme variable d'environnement : héritée par tous les processus enfants
  # (Maven → Surefire → JMH fork) sans aucun filtrage
  export RAG_SOURCE_DIR="$SOURCE_DIR"
  REAL_SOURCE_PROP="-Drag.source.dir=${SOURCE_DIR}"
else
  REAL_SOURCE_PROP=""
  if [[ -n "$CUSTOM_FILE_COUNTS" ]]; then
    FILE_COUNTS="$CUSTOM_FILE_COUNTS"
  elif [[ "$FULL" == "true" ]]; then
    FILE_COUNTS="$FILE_COUNTS_FULL"
  else
    FILE_COUNTS="$FILE_COUNTS_QUICK"
  fi
fi

# ── Répertoire de résultats horodaté ──────────────────────────────────────────
RUN_ID="$(date +%Y-%m-%d_%H-%M)"
RESULTS_DIR="target/benchmark-results/${RUN_ID}"
mkdir -p "$RESULTS_DIR"

# ── Récapitulatif avant lancement ─────────────────────────────────────────────
sep
echo -e "${BOLD}RAG Benchmark Runner${NC}"
sep
if [[ -n "$SOURCE_DIR" ]]; then
  log "Mode          : réel (codebase existante)"
  log "Source        : ${SOURCE_DIR}"
else
  log "Mode          : $( [[ "$FULL" == "true" ]] && echo "complet" || echo "rapide" ) (sources synthétiques)"
  log "Tailles       : ${FILE_COUNTS}"
fi
log "Scénarios     : ${SCENARIOS//,/ | }"
log "Juge LLM      : $( [[ "$JUDGE_ENABLED" == "true" ]] && echo "activé" || echo "désactivé" )"
log "Indexation    : $( [[ "$WITH_INDEXATION" == "true" ]] && echo "oui" || echo "non" )"
log "Résultats     : ${RESULTS_DIR}/"
sep

# Avertissement durée si mode complet
if [[ "$FULL" == "true" ]]; then
  warn "Mode complet sélectionné — durée estimée :"
  warn "  Retrieval  : ~30–45 min (4 scénarios × 4 tailles)"
  warn "  Indexation : ~3h+ (dominé par Neo4j 10000 fichiers)"
  echo
  read -r -p "  Continuer ? [y/N] " confirm
  [[ "${confirm,,}" =~ ^y ]] || { log "Annulé."; exit 0; }
  echo
fi

# Avertissement modèle juge
if [[ "$JUDGE_ENABLED" == "true" ]]; then
  warn "Le juge LLM nécessite qwen2.5:14b via Ollama (configurable avec -Djmh.judge.model=)."
  warn "Désactiver avec --no-judge si le modèle n'est pas disponible."
  echo
fi

# ── Compiler ──────────────────────────────────────────────────────────────────
sep
log "Compilation..."
mvn test-compile -q || die "Échec de la compilation."
ok "Compilation OK"

# ── Nettoyer l'ancien fichier juge (accumulation propre) ─────────────────────
rm -f target/jmh-judge.jsonl

# ── Propriétés JMH communes ───────────────────────────────────────────────────
JUDGE_PROP="-Djmh.judge.enabled=${JUDGE_ENABLED}"
PARAMS_PROP="-Djmh.params=scenario=${SCENARIOS};fileCount=${FILE_COUNTS}"
SOURCE_PROP="${REAL_SOURCE_PROP}"

# ── Phase 1 : Benchmark d'indexation (optionnel) ─────────────────────────────
if [[ "$WITH_INDEXATION" == "true" ]]; then
  sep
  log "Phase 1 / 2 — Indexation..."
  IDX_RESULT="${RESULTS_DIR}/jmh-indexation.json"

  mvn test -Dtest=BenchmarkRunner#indexation \
    "-Djmh.result=${IDX_RESULT}" \
    "-Djmh.params=fileCount=${FILE_COUNTS}" \
    -q 2>&1 | tee "${RESULTS_DIR}/indexation.log"

  cp -f target/jmh-indexation.json "${IDX_RESULT}" 2>/dev/null || true
  ok "Indexation terminée → ${IDX_RESULT}"
fi

# ── Phase 2 : Benchmark de retrieval ─────────────────────────────────────────
sep
PHASE=$( [[ "$WITH_INDEXATION" == "true" ]] && echo "2 / 2" || echo "1 / 1" )
log "Phase ${PHASE} — Retrieval ($(echo "$SCENARIOS" | tr ',' '\n' | wc -l | tr -d ' ') scénarios × $(echo "$FILE_COUNTS" | tr ',' '\n' | wc -l | tr -d ' ') tailles)..."

RET_RESULT="${RESULTS_DIR}/jmh-retrieval.json"

mvn test -Dtest=BenchmarkRunner#retrieval \
  "-Djmh.result=${RET_RESULT}" \
  "${PARAMS_PROP}" \
  "${JUDGE_PROP}" \
  ${SOURCE_PROP:+"${SOURCE_PROP}"} \
  -q 2>&1 | tee "${RESULTS_DIR}/retrieval.log"

cp -f target/jmh-retrieval.json "${RET_RESULT}" 2>/dev/null || true
[[ -f target/jmh-judge.jsonl ]] && cp -f target/jmh-judge.jsonl "${RESULTS_DIR}/jmh-judge.jsonl"

ok "Retrieval terminé → ${RET_RESULT}"

# ── Sauvegarder la config du run ──────────────────────────────────────────────
cat > "${RESULTS_DIR}/run.config" <<EOF
date=$(date -Iseconds)
mode=$( [[ -n "$SOURCE_DIR" ]] && echo "real" || ( [[ "$FULL" == "true" ]] && echo "full" || echo "quick" ) )
scenarios=${SCENARIOS}
fileCount=${FILE_COUNTS}
sourceDir=${SOURCE_DIR:-synthetic}
judgeEnabled=${JUDGE_ENABLED}
withIndexation=${WITH_INDEXATION}
EOF

# ── Résumé final ──────────────────────────────────────────────────────────────
sep
echo -e "${BOLD}${GREEN}Benchmark terminé !${NC}"
echo
echo -e "  Résultats : ${BOLD}${RESULTS_DIR}/${NC}"
echo
echo -e "  Fichiers sauvegardés :"
ls "${RESULTS_DIR}/" | while read -r f; do
  SIZE=$(wc -c < "${RESULTS_DIR}/${f}" 2>/dev/null | tr -d ' ')
  printf "    %-30s %s\n" "$f" "$(numfmt --to=iec-i --suffix=B "$SIZE" 2>/dev/null || echo "${SIZE}B")"
done
echo
echo -e "  Pour visualiser, ouvre dans ton navigateur :"
echo -e "    ${BOLD}dashboard/index.html${NC}"
echo -e "  puis charge : ${BOLD}${RET_RESULT}${NC}"
[[ -f "${RESULTS_DIR}/jmh-judge.jsonl" ]] && \
  echo -e "          et  : ${BOLD}${RESULTS_DIR}/jmh-judge.jsonl${NC}"
sep
