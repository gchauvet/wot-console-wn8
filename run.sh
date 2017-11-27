#!/usr/bin/env bash

cd "${0%/*}"

source ./bin/activate

python3.6 run.py

deactivate
