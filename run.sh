#!/usr/bin/env bash

cd "${0%/*}"

source ./bin/activate

python3.6 main

deactivate

printf "Task complete.\n\n\n"
