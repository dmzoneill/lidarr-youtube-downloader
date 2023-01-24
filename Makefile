.PHONY: all

all: clean push

SHELL := /bin/bash
CWD := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

lint:
	black -v *.py
	black -v lidarr_youtube_downloader/*.py

clean: lint
	rm -rvf dist
	
bump: clean
	version=$(grep '^Version:' PKG-INFO | sed 's/Version: //')
	next=$(echo $version | awk -F. '/[0-9]+\./{$NF++;print}' OFS=.)
	sed "s/$version/$next/" -i PKG-INFO
	sed "s/$version/$next/" -i pyproject.toml
	sed "s/$version/$next/" -i setup.py

upload: bump
	python3 -m pip install --upgrade build
	python3 -m pip install --upgrade twine
	python3 -m build
	python3 -m twine upload --repository pypi dist/*

push: clean
	git add -A
	git commit --amend --no-edit 
	git push -u origin main:main -f
