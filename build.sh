BASEDIR=$(dirname $0)
pushd $BASEDIR
xh-py-project-version sync-dependencies
rm -fr dist/*
python -m build
popd