.PHONY: install up down migrate seed test lint format schema check offline-bundle

install:            ## Dépendances backend + frontend
	cd backend && pip install -r requirements/dev.txt
	cd frontend && npm ci

up:                 ## MySQL seul (optionnel : SQLite suffit pour débuter)
	docker compose up -d db

down:
	docker compose down

migrate:
	cd backend && python manage.py migrate

seed:               ## Rôles et permissions
	cd backend && python manage.py seed_roles

test:               ## Tests backend (+ architecture) et frontend
	cd backend && DJANGO_SETTINGS_MODULE=config.settings.test python -m pytest
	cd frontend && npm test

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run typecheck

format:
	cd backend && ruff format .

schema:             ## Régénère le contrat OpenAPI puis les types TypeScript
	cd backend && DJANGO_SETTINGS_MODULE=config.settings.test python manage.py spectacular --file ../contracts/openapi/schema.yaml --validate --fail-on-warn
	cd frontend && npm run api:types

check: lint test    ## À lancer avant chaque Pull Request

offline-bundle:     ## (machine AVEC Internet) prépare le dossier à copier sur un serveur SANS Internet
	./scripts/offline/prepare-bundle.sh
