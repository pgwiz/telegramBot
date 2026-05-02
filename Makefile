.PHONY: install dev run lint test fmt docker

VENV ?= .venv
PY   ?= $(VENV)/bin/python
PIP  ?= $(VENV)/bin/pip

install:
	python -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

dev: install
	$(PIP) install -r requirements-dev.txt

run:
	PYTHONPATH=src $(PY) src/bot.py

lint:
	$(VENV)/bin/ruff check src tests

fmt:
	$(VENV)/bin/ruff format src tests

test:
	PYTHONPATH=src $(VENV)/bin/pytest -q

docker:
	docker build -t telegram-bot:latest .
