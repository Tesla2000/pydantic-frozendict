setup: uv git_init precommit_install git_add

precommit_install:
	pre-commit install --hook-type pre-commit --hook-type pre-push
	pre-commit autoupdate

git_init:
	git init

git_add:
	git add .
	git commit -m "initial commit"

uv:
	uv sync

.PHONY: setup
