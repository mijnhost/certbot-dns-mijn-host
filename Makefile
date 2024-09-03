lint:
	ruff check --config ruff.toml

lint-fix:
	ruff check --config ruff.toml --fix

format:
	ruff format

test:
	python -m unittest ./certbot_dns_mijn_host/test_mijn_host.py 

build:
	python setup.py sdist bdist_wheel

install-local:
	pip install --use-pep517 -e .
