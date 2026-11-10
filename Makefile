PYTHON ?= python3
CSV    := results/resultados.csv

.PHONY: all run test analyze clean help

all: run

run:
	@mkdir -p results
	$(PYTHON) src/benchmark.py --csv $(CSV)

test:
	$(PYTHON) src/test_lcs.py

analyze: run
	$(PYTHON) src/analyze.py --csv $(CSV) --out results/tablas.tex
	@echo "Tablas generadas en results/tablas.tex"

clean:
	rm -rf results
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

help:
	@echo "make run     - ejecuta benchmarks (CSV + graficas)"
	@echo "make test    - pruebas de correctitud"
	@echo "make analyze - vuelca Tablas 2 y 3 en LaTeX"
	@echo "make clean   - limpia artefactos"
