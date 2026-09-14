# Judge fine-tuning pipeline — tout en local (Apple Silicon / MLX).
# Aide : make help

VENV       := .venv
PY         := $(VENV)/bin/python
LORA       := $(VENV)/bin/mlx_lm.lora
SEED       := $(wildcard data/seed/*.jsonl)
CONFIG     := configs/variants.json
GOLDEN     := data/golden/test.jsonl
OUT        := results

MODEL_14B  := mlx-community/Qwen2.5-Coder-14B-Instruct-4bit
MODEL_32B  := mlx-community/Qwen2.5-Coder-32B-Instruct-4bit
MODEL_MINI := mlx-community/Qwen2.5-Coder-0.5B-Instruct-4bit

# Hyperparamètres identiques pour les deux tailles (comparaison équitable).
TEST_SIZE  ?= 50
ITERS      ?= 400
NUM_LAYERS ?= 16
LR         ?= 1e-5
MAXLEN     ?= 2048
LORA_ARGS   = --train --fine-tune-type lora --mask-prompt --batch-size 1 --grad-checkpoint \
              --num-layers $(NUM_LAYERS) --iters $(ITERS) --learning-rate $(LR) \
              --max-seq-length $(MAXLEN) --steps-per-report 10 --steps-per-eval 50 \
              --val-batches -1 --seed 42

.PHONY: help setup validate stats split split-poc smoke smoke-bench smoke-all train-14b train-32b \
        bench bench-14b bench-32b report clean-results clean

help:
	@echo "Dataset :  make validate | make stats | make split | make split-poc"
	@echo "Pipeline:  make smoke-all             (fine-tuning + service + benchmark sur 0.5B, ~3 min)"
	@echo "Training:  make train-14b | make train-32b"
	@echo "Benchmark: make bench-14b | make bench-32b | make bench | make report"
	@echo "Variables: TEST_SIZE=$(TEST_SIZE) ITERS=$(ITERS) NUM_LAYERS=$(NUM_LAYERS) LR=$(LR) MAXLEN=$(MAXLEN)"

setup:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q --upgrade pip
	$(VENV)/bin/pip install -q mlx-lm
	@$(PY) -c "import mlx_lm; print('mlx-lm', mlx_lm.__version__, 'installé')"

# Régénère les lots depuis leurs générateurs. Déterministe : sert aussi à réparer
# un fichier corrompu, les JSONL n'étant jamais édités à la main.
regen:
	@for n in 01 02 03 04 05 06 07 08 09 10 11; do \
	  $(PY) generators/gen_batch_$$n.py data/seed/batch_$$n.jsonl; \
	done
	@$(MAKE) --no-print-directory validate

validate:
	$(PY) scripts/dataset_tools.py validate $(SEED)

stats:
	$(PY) scripts/dataset_tools.py stats $(SEED)

split: validate
	$(PY) scripts/dataset_tools.py split $(SEED) --out data --test-size $(TEST_SIZE)

split-poc:
	$(MAKE) split TEST_SIZE=10

# Valide toute la chaîne (données -> entraînement -> service -> benchmark) sur un modèle
# minuscule : aucune conclusion qualité à en tirer, uniquement "ça tourne".
smoke:
	$(LORA) --model $(MODEL_MINI) --data data/mlx-smoke --adapter-path adapters/smoke-0.5b \
	        $(LORA_ARGS) --num-layers 4 --iters 20 --steps-per-report 5 --steps-per-eval 10 --val-batches 1

# Même validation, côté service : serveur + adapter + client HTTP + calcul des métriques.
smoke-bench:
	CONFIG=configs/variants.smoke.json GOLDEN=data/seed/batch_01.jsonl OUT=results-smoke \
	  ./scripts/bench_variant.sh smoke-0.5B --passes 1 --bootstrap 200

smoke-all: smoke smoke-bench

# Sans ce garde-fou, mlx-lm prend "data/mlx" pour un dataset Hugging Face et échoue
# sur un ModuleNotFoundError: datasets, qui n'a rien à voir avec la vraie cause.
data/mlx/train.jsonl:
	@echo "ERREUR : data/mlx/train.jsonl absent. Lance d'abord 'make split' (ou 'make split-poc')." >&2
	@exit 1

train-14b: data/mlx/train.jsonl
	$(LORA) --model $(MODEL_14B) --data data/mlx --adapter-path adapters/14b-judge $(LORA_ARGS)

train-32b: data/mlx/train.jsonl
	$(LORA) --model $(MODEL_32B) --data data/mlx --adapter-path adapters/32b-judge $(LORA_ARGS)

# Une variante à la fois : le serveur est démarré puis arrêté par le script.
bench-14b:
	./scripts/bench_variant.sh 14B-baseline
	./scripts/bench_variant.sh 14B-finetuned

bench-32b:
	./scripts/bench_variant.sh 32B-baseline
	./scripts/bench_variant.sh 32B-finetuned

bench: bench-14b bench-32b report

report:
	$(PY) scripts/benchmark_judges.py --config $(CONFIG) --golden $(GOLDEN) --out $(OUT) --report-only
	@echo "Rapport : $(OUT)/report.md"

clean-results:
	rm -rf $(OUT)

clean: clean-results
	rm -rf $(VENV) adapters data/mlx data/golden data/mlx-smoke
