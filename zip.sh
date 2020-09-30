#!/bin/sh

cd "$(dirname "$0")"

# Zips the executable
cp -v -f -R dist ctjs-installer-linux
mkdir zip
# zip ctjs-installer-linux ctjs-installer-linux/*
# mv ctjs-installer-linux.zip zip
mv ctjs-installer-linux/* zip
