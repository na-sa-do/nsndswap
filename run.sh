#!/usr/bin/env bash

set -eu
if [[ -d output ]]; then
    echo Erasing output directory
    rm -r output
fi
mkdir output

echo Starting Python script
python3 -m nsndswap

cd gephibridge
export CLASSPATH='.:lib/*'
javac GephiBridge.java
for f in ../output/*.gexf ; do
    java GephiBridge "$f"
done
