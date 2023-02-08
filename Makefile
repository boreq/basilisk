ci: dev-dependencies mypy pyflakes test

dev-dependencies:
	pip install -e ".[dev]"
.PHONY: dev-dependencies

test:
	py.test -s tests
.PHONY: test

mypy:
	#mypy --warn-no-return --disallow-untyped-defs basilisk
	mypy basilisk
.PHONY: mypy

pyflakes:
	pyflakes basilisk
.PHONY: pyflakes
