IMAGE:=django-reference
DATE:=$(shell date "+%Y%m%d%H%M")

TAGGED_IMAGE:=$(IMAGE):$(DATE)

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
	docker build -t $(IMAGE) -t $(TAGGED_IMAGE) .

.PHONY: run-local
run-local: ## Run the Django Docker locally on port 8000
run-local:
	docker-compose up -d

.PHONY: push
push: ## Push new docker image to docker hub
	docker build -t $(IMAGE) -t $(TAGGED_IMAGE) -t simplecto/$(TAGGED_IMAGE)  .
	docker push simplecto/$(TAGGED_IMAGE)