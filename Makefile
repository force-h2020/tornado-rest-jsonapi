SHELL=bash

.PHONY: venv
venv:
	@echo "Creating virtual environment"
	@echo "----------------------------"
	python3 -m venv venv

.PHONY: aptdeps
aptdeps:
	@echo "Installing apt dependencies"
	@echo "---------------------------"
	apt-get update
	apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y python3-pip python3.4-venv
	pip install --upgrade pip

.PHONY: pythondeps
pythondeps:
	@echo "Installing dependencies"
	@echo "-----------------------"
	pip3 install -r requirements.txt

.PHONY: devdeps
devdeps:
	@echo "Installing dependencies"
	@echo "-----------------------"
	pip3 install -r dev-requirements.txt -r doc-requirements.txt

.PHONY: develop
develop: 
	@echo "Installing application"
	@echo "----------------------"
	python3 setup.py develop

.PHONY: install
install:
	@echo "Installing application"
	@echo "----------------------"
	python3 setup.py install

.PHONY: test
test:
	@echo "Running testsuite"
	@echo "-----------------"
	flake8 . && python -m tornado.testing discover -s tornadowebapi -t . -v

.PHONY: docs
docs:
	sphinx-build -W doc/source doc/build/sphinx
