#! /bin/bash

VERSION=0.3.2

# cleanup

find . -type d -name __pycache__ | xargs rm -rf

# create archive

cd ..
tar \
    --exclude-vcs \
    --exclude=data \
    --exclude=debian \
    --exclude=.pc \
    --exclude=*~ \
    --exclude=pyproject.toml \
    --exclude=poetry.lock \
    -zcvf python-magnetgeo_$VERSION.orig.tar.gz python_magnetgeo
