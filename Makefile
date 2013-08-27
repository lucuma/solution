.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "publish - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

lint:
	flake8 solution tests

test:
	py.test tests/

test-all:
	tox

coverage:
	py.test --cov-config .coveragerc --cov-report html --cov solution tests/ 
	open htmlcov/index.html

docs:
	rm docs/solution.rst
	rm docs/modules.rst
	sphinx-apidoc -o docs/ solution
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

publish: clean
	python setup.py sdist upload

sdist: clean
	python setup.py sdist
	ls -l dist
