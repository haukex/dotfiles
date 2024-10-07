
SHELL = /bin/bash
.ONESHELL:  # each recipe is executed as a single script

.PHONY: test
test:
	@set -euxo pipefail
	mypy ./*.py
	shellcheck ./*.sh

.PHONY: installdeps
installdeps:
	@set -euxo pipefail
	python -m pip install --upgrade --upgrade-strategy=eager pip wheel
	python -m pip install 'colorama>=0.4.6' 'igbpyutils>=0.6.0'
	python -m pip install mypy types-colorama
