#!/bin/sh
for f in src/*.ui; do
    pyuic5 $f -o $(basename -s .ui $f).py
done
