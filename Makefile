.PHONY: test build publish-test release clean

test:
	pre-commit run --all-files --show-diff-on-failure

build: clean
	python -m build

publish-test: build
	twine check dist/*
	twine upload --repository testpypi dist/* --skip-existing

# Usage: make release VERSION=0.2.5
release: test publish-test
	git add src/lovethedocs/__init__.py pyproject.toml
	git commit -m "Bump version to $(VERSION)"
	git tag -a v$(VERSION) -m "v$(VERSION)"
	git push origin main --follow-tags

clean:
	rm -rf build dist src/lovethedocs.egg-info