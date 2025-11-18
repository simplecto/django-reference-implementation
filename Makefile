include config.mk

##########################################################################
# MENU
##########################################################################
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

data/:
	mkdir -p data/

env:
	cp env.example env

.venv/: data/ env
	python -m venv .venv/
	source venv/bin/activate && pip install --upgrade pip
	source venv/bin/activate && pip install -r requirements.txt
	source venv/bin/activate && pip install -r requirements-dev.txt
	source venv/bin/activate && pre-commit install

.PHONY: migrate
migrate: ## Run Django migrations
	docker compose run -it --rm django ./manage.py migrate

.PHONY: superuser
superuser: ## Create a superuser
	docker compose run -it --rm django ./manage.py createsuperuser

.PHONY: dev-bootstrap
dev-bootstrap: .venv/ ## Bootstrap the development environment
	docker compose pull
	docker compose build
	docker compose up -d postgres
	$(MAKE) migrate
	$(MAKE) superuser
	docker compose down

.PHONY: dev-start
dev-start: ## Start the development environment
	docker compose up -d
	sleep 5
	curl --request PUT http://localhost:9000/testbucket

.PHONY: dev-stop
dev-stop: ## Stop the development environment
	docker compose down

.PHONY: dev-restart-django
dev-restart-django: ## Restart the Django service
	docker compose up -d --force-recreate django

.PHONY: snapshot-local-db
snapshot-local-db: ## Create a snapshot of the local database
	docker compose exec postgres pg_dump -U postgres -Fc django_reference > django_reference.dump

.PHONY: restore-local-db
restore-local-db: ## Restore the local database from a snapshot
	docker compose exec -T postgres pg_restore -U postgres -d django_reference < django_reference.dump

logs/:
	mkdir -p logs/

.PHONY: runserver
runserver: logs/ ## Run Django development server with logging to logs/server.log
	@echo "Starting Django server on http://0.0.0.0:8008 (logs: logs/server.log)"
	uv run src/manage.py runserver 0.0.0.0:8008 2>&1 | tee logs/server.log

##########################################################################
# DJANGO-ALLAUTH DEPENDENCY MANAGEMENT
##########################################################################

.PHONY: dev-allauth
dev-allauth: ## Switch to local editable django-allauth install (if workspace exists)
	@echo "⚠️  Local development not fully working yet - use prod-allauth instead"
	@exit 1

.PHONY: prod-allauth
prod-allauth: ## Switch to remote git django-allauth source
	-uv remove django-allauth
	uv add "django-allauth[mfa,socialaccount] @ git+https://github.com/heysamtexas/django-allauth.git@heysamtexas-patches"
	@echo "✅ Switched to remote git django-allauth"

.PHONY: allauth-status
allauth-status: ## Show current django-allauth source
	@echo "Current django-allauth dependency:"
	@grep "django-allauth" pyproject.toml || echo "django-allauth not found in pyproject.toml"
