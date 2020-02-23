##########################################################################
# MENU
##########################################################################
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv/:
	python -m venv venv/
	source venv/bin/activate && pip install --upgrade pip

.PHONY: boostrap-dev
bootstrap-dev: venv/ ## Bootstrap the local development environment

.PHONY: build
build: ## Build the Django Docker image locally
	docker build -t django .

.PHONY: run-local
run-local: ## Run the Django Docker locally on port 8000
run-local:
	docker-compose up -d
