@_default:
    just --list

# Build a development environment
devenv:
    uv sync --extra dev --refresh --upgrade

# Wipe devenv and build artifacts
clean:
    rm -rf .venv uv.lock
    rm -rf build dist src/paul_mclendahand.egg-info .tox
    find src/ -name __pycache__ | xargs rm -rf
    find src/ -name '*.pyc' | xargs rm -rf

# Run tests
test: devenv
    uv run tox

# Format files
format: devenv
    uv run tox exec -e py39-lint -- ruff format

# Lint files
lint: devenv
    uv run tox -e py39-lint

# Build docs
docs: devenv
    tox exec -e py39 -- cog -r README.rst

# Build release packages
build: devenv
    rm -rf build/ dist/
    uv run python -m build
    uv run twine check dist/*
