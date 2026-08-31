.PHONY: db-migrate db-status db-clear db-reset db-seed artifacts-clean

BACKEND_DIR := backend
PYTHON := .venv/bin/python

db-migrate:
	cd $(BACKEND_DIR) && $(PYTHON) -m scripts.db migrate

db-status:
	cd $(BACKEND_DIR) && $(PYTHON) -m scripts.db status

db-clear:
	cd $(BACKEND_DIR) && $(PYTHON) -m scripts.db clear

db-reset:
	cd $(BACKEND_DIR) && $(PYTHON) -m scripts.db reset

db-seed:
	cd $(BACKEND_DIR) && $(PYTHON) -m scripts.db seed $(FILE)

artifacts-clean:
	cd $(BACKEND_DIR) && $(PYTHON) -m scripts.db clear-artifacts
