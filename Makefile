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
	wget https://omnivector-public-assets.s3.us-west-2.amazonaws.com/charms/charm-jobbergate/edge/jobbergate.charm?response-content-disposition=attachment&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQDbjOv7Z4PonSRl0872owiNKc22Frqt6Kykl3g31C2IJAIgeFhSduCgqOMj54qs005khgDdxDsFQptv68CMuoFKVk8q2wIIIBABGgwyMTIwMjE4Mzg1MzEiDPv37Rau24HewGbQpCq4Al5ymLJgHRLiiAPzWsn9focBkk4RO6TelxPEPt1qe8S0UypUMX16uiehXue8Ud8XbO4cSpg%2FG7c8VyCQQ66vV7LFELBwE6RXzPID1L2XusWmKMpfryfU3bzh42Ce2EHAHpquHthzWRrSDcyawWR6p72KRBR%2F5%2BdZ6PTgEoPuthr%2FB7ajfIvSbJWJcqRk8YyuDKBbUvC%2F6DuKqxx3YFl%2F7eoZ%2Btw4robut7qxLizMTKSEaGtcD7HpwkZI6KEARyZDc5D4Bxs0JfS714nBhZXMuZB9g7%2BjHV3ea47oP%2FMeWNRXg8P4JsouIS0MAlDTCQxyk7aV5%2BFF45SbR7cMGT3Y9zaBJA0EKGmI7gD1%2FNV8a%2BR5CXEywS7ckLzUKwdG89JXmS0cDcspZg2HNbc5T0fC1U0Vr1nFWh0waDD9iMz9BTqwApdedMUzZa4nu3dC6Xp6Szqnrro86yyoCq3pYW%2BVQUhM4TFo3j57KB%2BQSRQsfDAP8NCy2dhlAiKEubvmlUHzHdGr0z3pmI9%2BverM9ibMOQp0sNW%2FZEp9snEy8JwZX5S3Z2zUSuDCFJWKBFmoOyAZScajhp3v16mqJwHp9arPDcMOmt5KLCYLv99FTxRwzf4x62RIuaFv7OD23Zt%2BV7YJErCJ%2FizO6cxWC9h1ubyAshnKzS71rQiluYqDBT1iZnIoG%2FuY%2Fm93Bua54bsCZxjS6JRUeU00gYK3vYo9Nqg3cpBRu%2FxoYYffKWAYTC9kHrILMhZ8yZfPC1AKGd9crr925ErtmEDfodLlv38FuljxVutpElfpc%2FGaP%2BdyFSwgSyBkwqC1eiWgKwnX0Lp1yQoTLgE%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201116T231437Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIATCXL4QLB25WYSFGX%2F20201116%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=09ccee5e37199f81e9b506c09e003380439c649c727c98657e065b0f1340b651

# SETTINGS
# Use one shell for all commands in a target recipe
.ONESHELL:
# Set default goal
.DEFAULT_GOAL := help
# Use bash shell in Make instead of sh 
SHELL := /bin/bash
