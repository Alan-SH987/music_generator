BACKEND := backend
FRONTEND := frontend
VENV := $(BACKEND)/.venv

.DEFAULT_GOAL := help
.PHONY: help install install-backend install-frontend backend frontend test lint typecheck build up down logs clean

help: ## Show this help
	@echo "Royalty-Free Music Generator — make targets:"
	@echo "  install            Install backend (venv + dev deps) and frontend deps"
	@echo "  backend            Run the FastAPI backend on http://localhost:8000"
	@echo "  frontend           Run the Next.js frontend on http://localhost:3000"
	@echo "  test               Run the backend pytest suite"
	@echo "  lint               Lint the backend with ruff"
	@echo "  typecheck          Type-check the frontend with tsc"
	@echo "  build              Production build of the frontend"
	@echo "  up / down          Start / stop the full stack with Docker Compose"
	@echo "  logs               Follow Docker Compose logs"
	@echo "  clean              Remove venv, node_modules and build caches"

install: install-backend install-frontend ## Install everything

install-backend:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r $(BACKEND)/requirements-dev.txt

install-frontend:
	cd $(FRONTEND) && npm install

backend:
	cd $(BACKEND) && .venv/bin/uvicorn app.main:app --reload --port 8000

frontend:
	cd $(FRONTEND) && npm run dev

test:
	cd $(BACKEND) && .venv/bin/pytest

lint:
	cd $(BACKEND) && .venv/bin/ruff check .

typecheck:
	cd $(FRONTEND) && npx tsc --noEmit

build:
	cd $(FRONTEND) && npm run build

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	rm -rf $(VENV) $(FRONTEND)/node_modules $(FRONTEND)/.next $(BACKEND)/.pytest_cache $(BACKEND)/.ruff_cache
	find $(BACKEND) -type d -name __pycache__ -prune -exec rm -rf {} +
