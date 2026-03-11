SHELL := /bin/bash

# Use system Python3 by default. For isolated dev environment, use 'make setup-uv'
PYTHON := python3
PIP := pip3
PYTEST := pytest

.PHONY: help setup-uv install-uv test test-notebook collect-once collect-live notebook clean clean-cache clean-uv

help:
	@echo "Available targets:"
	@echo "  make setup-uv      - create uv venv and install all dependencies"
	@echo "  make install-uv    - install/update dependencies in uv venv"
	@echo "  make test          - run unit tests (uses system python)"
	@echo "  make test-notebook - run unit tests with notebook dependencies"
	@echo "  make collect-once  - run one data collection cycle (+ kline backfill)"
	@echo "  make collect-live  - run continuous polling every 60 seconds"
	@echo "  make notebook      - open Jupyter Notebook (requires notebook deps)"
	@echo "  make clean         - remove python cache artifacts"
	@echo "  make clean-uv      - remove uv venv and cache"
	@echo ""
	@echo "Lightweight mode (no venv):"
	@echo "  - 'make test' uses system python3 + pip3"
	@echo "  - Install deps: pip3 install -r requirements.txt"
	@echo "  - Run scripts: python3 scripts/poll_orderbooks.py --once"

# UV-based setup (optional, for isolated environment)
setup-uv:
	@command -v uv >/dev/null 2>&1 || { echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv venv
	uv sync --extra dev --extra notebook

install-uv:
	@command -v uv >/dev/null 2>&1 || { echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync --extra dev --extra notebook

test:
	PYTHONPATH="$(shell pwd)" python3 -m pytest -q

test-notebook:
	PYTHONPATH="$(shell pwd)" python3 -m pytest -q

collect-once:
	PYTHONPATH="$(shell pwd)" python3 scripts/poll_orderbooks.py --output-dir data/raw --once --backfill-klines

collect-live:
	PYTHONPATH="$(shell pwd)" python3 scripts/poll_orderbooks.py --output-dir data/raw --interval-seconds 60

notebook:
	@echo "Notebook requires pandas/matplotlib/jupyter. Install with:"
	@echo "  pip3 install pandas numpy matplotlib seaborn ipywidgets jupyter"
	@echo "Or use uv: make setup-uv && make notebook"
	jupyter notebook

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

clean-uv:
	rm -rf .venv
	rm -rf .pytest_cache
	uv cache clean