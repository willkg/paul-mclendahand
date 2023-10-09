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
	rm -rf build dist src/${PROJECT}.egg-info .tox
	rm -rf docs/_build/*
	find src/ -name __pycache__ | xargs rm -rf
	find src/ -name '*.pyc' | xargs rm -rf

.PHONY: lint
lint:  ## Lint and black reformat files
	black src tests
	tox -e py38-lint

.PHONY: docs
docs:  ## Regenerate README
	tox exec -e py38 -- cog -r README.rst
