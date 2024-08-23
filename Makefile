##########################################################################
# MENU
##########################################################################
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv/:
	python -m venv venv/
	source venv/bin/activate && pip install --upgrade pip


.PHONY: migrate
migrate: ## Run Django migrations
	docker compose run -it --rm django ./manage.py migrate

.PHONY: superuser
superuser: ## Create a superuser
	docker compose run -it --rm django ./manage.py createsuperuser

.PHONY: dev-bootstrap
dev-bootstrap: ## Bootstrap the development environment
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
