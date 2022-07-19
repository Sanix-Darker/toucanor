.DEFAULT_GOAL=help

venv:
	pip install -U pip poetry

##install: setup your prod environment
install: venv
	poetry install --no-dev

##run: run the game
run:
	sudo python3 -m main

##pres: To start the presentation
pres:
	cat prez/*.md | slides

##install-dev: setup your dev environment
install-dev: venv
	poetry install

format:
	poetry run isort *.py
	poetry run black *.py

lint:
	poetry run flake8 *.py --show-source --statistics
	poetry run isort *.py --check-only --df
	poetry run black *.py --check --diff

##test: test your code
test: install-dev
	poetry run pytest

##help: show help
help : Makefile
	@sed -n 's/^##//p' $<

.PHONY : help venv install test lint
