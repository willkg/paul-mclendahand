DEFAULT_GOAL := help
PROJECT=paul_mclendahand

.PHONY: help
help:
	@echo "Available rules:"
	@fgrep -h "##" Makefile | fgrep -v fgrep | sed 's/\(.*\):.*##/\1:  /'

.PHONY: test
test:  ## Run tests
	tox

.PHONY: clean
clean:  ## Clean build artifacts
	rm -rf build dist ${PROJECT}.egg-info .tox
	rm -rf docs/_build/*
	find ${PROJECT}/ -name __pycache__ | xargs rm -rf
	find ${PROJECT}/ -name '*.pyc' | xargs rm -rf

.PHONY: lint
lint:  ## Lint and black reformat files
	black --target-version=py36 ${PROJECT}
	flake8 ${PROJECT}
