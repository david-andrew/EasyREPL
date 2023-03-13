# clear dist folder
rm -rf dist

# build and publish package to pypi
python -m build
python -m twine upload dist/*