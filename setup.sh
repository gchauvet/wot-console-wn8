#!/usr/bin/env bash

cd "${0%/*}"

python3.6 -m venv .
source ./bin/activate
pip3 install requests pandas

python3.6 main/initialize_database.py
python3.6 main/m_config.py

deactivate

echo "Setup complete."
