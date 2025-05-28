#!/bin/bash

# 1. Extract version from pyproject.toml
VERSION=$(tomlq -r '.project.version' pyproject.toml)
echo "Detected version: $VERSION"

# 2. Check if this version is already tagged
if git tag | grep -q "\b$VERSION\b"; then
  echo "Version $VERSION already exists. Exiting."
  exit 0
fi

# 3. Build and publish to PyPI
echo "Publishing version $VERSION..."

# Install dependencies
python3 -m pip install --upgrade build twine

# Build distribution
python3 -m build

# Upload to PyPI
twine upload dist/*

# 4. Tag release and push to Git
git tag "$VERSION"
git push origin "$VERSION"

echo "Release $VERSION published to PyPI and tagged in Git."
