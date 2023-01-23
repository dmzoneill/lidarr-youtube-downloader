.PHONY: all

all: clean push

SHELL := /bin/bash
CWD := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

clean: 
	rm -rvf dist

push: clean
	git add -A
	git commit --amend --no-edit 
	git push -u origin main:main -f

upload: clean
	python3 -m pip install --upgrade build
	python3 -m pip install --upgrade twine
	python3 -m build
	python3 -m twine upload --repository pypi dist/*
