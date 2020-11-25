.ONESHELL:
.DEFAULT_GOAL := help
SHELL := /bin/bash

export PATH := /snap/bin:$(PATH)


jobbergate.charm: src/charm.py metadata.yaml .jujuignore
	$(MAKE) clean
	charmcraft build


# TARGETS
lint: ## Run linter
	tox -e lint


clean: ## Remove .tox and build dirs
	rm -rf .tox/ venv/ build/
	rm -f jobbergate.charm


push-charm-to-edge: ## Remove .tox and build dirs
	aws s3 cp jobbergate.charm s3://omnivector-public-assets/charms/charm-jobbergate/edge/


pull-charm-from-edge: ## Remove .tox and build dirs
	wget https://omnivector-public-assets.s3-us-west-2.amazonaws.com/charms/charm-jobbergate/edge/jobbergate.charm


format:
	isort src
	black src
