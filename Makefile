VERSION=$(shell sed -n 's/^version = "\([0-9.]*\)"/\1/p' pyproject.toml)

build:
	python ../zinny-dev/bump_version.py
	python -m build

install:
	python -m pip install --upgrade .

test:
	python -m pytest tests

clean:
	rm -rf dist/ build/ src/zinny_api.egg-info

testpypi:
	python -m twine upload --repository testpypi dist/*

install-pypi:
	python -m pip install --index-url https://test.pypi.org/simple/ --no-deps zinny-api

pypi:
	python -m twine upload dist/*
	$(MAKE) tag

tag:
	# Create a Git tag with the current version and push it to the remote repository
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)

print-version:
	@echo $(VERSION)