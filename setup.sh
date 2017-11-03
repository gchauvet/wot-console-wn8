#!/usr/bin/env bash

cd "${0%/*}"

python3.6 -m venv .

source ./bin/activate

pip3.6 install -r requirements.txt

python3.6 scripts/init_database.py

#Create secret.py
DEST=main/secret.py
echo "#app_id to contact WG API services." > $DEST
echo "app_id = 'demo'" >> $DEST
echo "#List of hosts to push data to." >> $DEST
echo "hosts = [" >> $DEST
echo "    {'url': 'http://127.0.0.1:5000/update/', 'access_key': '12345'}" >> $DEST
echo "]" >> $DEST

deactivate

echo "Setup complete."
