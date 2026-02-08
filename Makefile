.PHONY: all lint test clean bump upload version push docker-build

all: lint test

SHELL := /bin/bash
CWD := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
version := $(shell grep '^Version:' PKG-INFO | sed 's/Version: //')
next := $(shell echo ${version} | awk -F. '/[0-9]+\./{$$NF++;print}' OFS=.)

lint:
	black -v lidarr_youtube_downloader/*.py
	black -v setup.py
	flake8 --max-line-length 120 setup.py lidarr_youtube_downloader/*.py || true

test:
	pytest -v

clean:
	rm -rvf dist build *.egg-info

bump: clean
	sed "s/$(version)/$(next)/" -i PKG-INFO
	sed "s/$(version)/$(next)/" -i pyproject.toml
	sed "s/$(version)/$(next)/" -i setup.py

upload: bump
	python3 -m pip install --upgrade build
	python3 -m pip install --upgrade twine
	python3 -m build
	python3 -m twine upload --repository pypi dist/*

version: upload clean
	git add -A
	git commit -a -m "Bump to $(next)"

docker-build:
	docker build -t lyd .

push:
	git push -u origin main:main
