
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
	python3 -m pip install --upgrade --upgrade-strategy=eager pip wheel
	python3 -m pip install 'colorama>=0.4.6' 'igbpyutils>=0.6.0'
	python3 -m pip install mypy types-colorama
