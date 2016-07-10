# System variables
VIRTUAL_ENV=$(CURDIR)/.env
PYTHON=$(VIRTUAL_ENV)/bin/python
COVERAGE=$(VIRTUAL_ENV)/bin/coverage
NOSE=$(VIRTUAL_ENV)/bin/nosetests


help:
# target: help - Display callable targets
	@grep -e "^# target:" [Mm]akefile | sed -e 's/^# target: //g'


.PHONY: clean
# target: clean - Display callable targets
clean:
	rm -rf build/ dist/ docs/_build *.egg-info \.coverage MANIFEST
	find $(CURDIR) -name "*.py[co]" -delete
	find $(CURDIR) -name "*.orig" -delete
	find $(CURDIR)/$(MODULE) -name "__pycache__" | xargs rm -rf


.PHONY: env
env:
# target: env - create virtualenv and install packages
	@virtualenv $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -r $(CURDIR)/requirements-test.txt


# ===============
#  Test commands
# ===============

.PHONY: test
test: env
# target: test - Run tests
	@$(NOSE) --with-coverage .


# ===============
#  Build package
# ===============

.PHONY: register
# target: register - Register package on PyPi
register:
	@$(VIRTUAL_ENV)/bin/python setup.py register


.PHONY: upload
upload: clean
# target: upload - Upload package on PyPi
	@$(VIRTUAL_ENV)/bin/pip install wheel
	@$(PYTHON) setup.py bdist_wheel upload -r pypi
