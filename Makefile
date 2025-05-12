# ----------  lovethedocs Makefile  ----------
.PHONY: test bump build publish-test release clean

# 1 ▸ Run exactly what CI runs
test:
	pre-commit run --all-files --show-diff-on-failure

# 2 ▸ Bump the version, commit, and sign a tag
#    Usage:  make bump VERSION=0.2.6
bump:
	@echo "Bumping to $(VERSION)"
	bump-my-version bump --new-version $(VERSION) --allow-dirty

# 3 ▸ Build a clean wheel + sdist
build: clean
	python -m build

# 4 ▸ Dry-run upload to Test PyPI
publish-test: build
	twine check dist/*
	twine upload --repository testpypi dist/* --skip-existing

# 5 ▸ One-shot release: bump → test → dry-run → push tags
#    Usage:  make release VERSION=0.2.6
release: bump test publish-test
	git push origin main --follow-tags

# 6 ▸ Clean build artefacts
clean:
	rm -rf build dist *.egg-info
# -------------------------------------------