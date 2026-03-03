SHELL := /bin/zsh

PROJECT_DIR := /Users/gilangfajar/Documents/Personal\ Files/Project/delomite/lima/
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
JUPYTER := $(VENV)/bin/jupyter
PYTEST := $(VENV)/bin/pytest

.PHONY: help setup install test test-system collect-once collect-live notebook clean

help:
	@echo "Available targets:"
	@echo "  make setup        - create venv and install dependencies"
	@echo "  make install      - install/update dependencies in existing venv"
	@echo "  make test         - run unit tests"
	@echo "  make test-system  - run unit tests with system python (fallback)"
	@echo "  make collect-once - run one data collection cycle (+ kline backfill)"
	@echo "  make collect-live - run continuous polling every 60 seconds"
	@echo "  make notebook     - open Jupyter Notebook"
	@echo "  make clean        - remove python cache artifacts"

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

setup: $(VENV)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt

test: $(VENV)/bin/activate
	PYTHONPATH="$(shell pwd)" PYTHONPYCACHEPREFIX=/tmp/pycache $(PYTEST) -q

test-system:
	PYTHONPATH="$(shell pwd)" PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m pytest -q

collect-once: $(VENV)/bin/activate
	PYTHONPYCACHEPREFIX=/tmp/pycache $(PYTHON) scripts/poll_orderbooks.py --output-dir data/raw --once --backfill-klines

collect-live: $(VENV)/bin/activate
	PYTHONPYCACHEPREFIX=/tmp/pycache $(PYTHON) scripts/poll_orderbooks.py --output-dir data/raw --interval-seconds 60

notebook: $(VENV)/bin/activate
	$(JUPYTER) notebook

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
