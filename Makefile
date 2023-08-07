# TARGETS
charm: clean version ## Build the charm
	@charmcraft pack
	@mv new-jobbergate-cli_*.charm new-jobbergate-cli.charm

lint: ## Run linter
	tox -e lint


clean: ## Remove .tox and build dirs
	rm -rf .tox/ venv/ build/
	rm -f *.charm
	rm -f version

version: ## Create/update version file
	@git describe --tags --dirty --always > version

format:
	isort src
	black src

# Display target comments in 'make help'
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# SETTINGS
# Use one shell for all commands in a target recipe
.ONESHELL:
# Set default goal
.DEFAULT_GOAL := help
# Use bash shell in Make instead of sh
SHELL := /bin/bash
