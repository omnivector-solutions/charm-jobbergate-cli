export PATH := /snap/bin:$(PATH)
  
# TARGETS
lint: ## Run linter
	tox -e lint

clean: ## Remove .tox and build dirs
	rm -rf .tox/
	rm -rf venv/

push-charm-to-edge: ## Remove .tox and build dirs
	aws s3 cp jobbergate.charm s3://omnivector-public-assets/charms/charm-jobbergate/edge/ 

pull-charm-from-edge: ## Remove .tox and build dirs
	wget https://omnivector-public-assets.s3-us-west-2.amazonaws.com/charms/charm-jobbergate/edge/jobbergate.charm

pull-snap-from-edge: ## Remove .tox and build dirs
	aws s3 cp s3://omnivector-private-assets/snaps/jobbergate-cli/edge/jobbergate-cli_0.0.1_amd64.snap ./jobbergate-cli.snap

# SETTINGS
# Use one shell for all commands in a target recipe
.ONESHELL:
# Set default goal
.DEFAULT_GOAL := help
# Use bash shell in Make instead of sh 
SHELL := /bin/bash
