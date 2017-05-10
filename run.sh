#!/usr/bin/env bash

set -eu

python3 -m nsndswap

cd gephibridge
export CLASSPATH='.:lib/*'
javac GephiBridge.java
for f in ../output/*.gexf ; do
    java GephiBridge "$f"
done
