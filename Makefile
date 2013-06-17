.PHONY: clean clean-pyc test upload

all: clean clean-pyc test

clean: clean-pyc
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -name '.DS_Store' -delete
	rm -rf tests/__pycache__
	rm -rf solution/__pycache__
	rm -rf solution/fields/__pycache__
	rm -rf solution/validators/__pycache__

clean-pyc:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete

test:
	py.test --cov-config .coveragerc --cov solution tests/

upload: clean
	python setup.py sdist upload

