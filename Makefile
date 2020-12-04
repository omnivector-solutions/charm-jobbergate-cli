.DEFAULT_GOAL 	:= help
SHELL			:= /bin/bash
.ONESHELL:
.PHONY: lint clean push-charm-to-edge pull-charm-from-edge format

export PATH 	:= /snap/bin:$(PATH)

SNAP_TARGET		:= jobbergate-cli.snap

-include jobbergate-cli/snap.mk


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


$(SNAP_TARGET):
	$(MAKE) -C jobbergate-cli $(SNAP_TARGET)


deploy-localhost: jobbergate.charm $(SNAP_TARGET)
	juju model-config logging-config="<root>=DEBUG;juju.worker.dependency=CRITICAL;unit=DEBUG"
	juju deploy ./jobbergate.charm --resource jobbergate-snap=$(SNAP_TARGET)


upgrade-localhost: jobbergate.charm $(SNAP_TARGET)
	juju model-config logging-config="<root>=DEBUG;juju.worker.dependency=CRITICAL;unit=DEBUG"
	juju upgrade-charm jobbergate --path=./jobbergate.charm --resource jobbergate-snap=$(SNAP_TARGET)
