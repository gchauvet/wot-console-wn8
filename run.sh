#!/usr/bin/env bash

#Change to current dir with this file.
cd "${0%/*}"

#Enter virtual environment.
source ./bin/activate


python3.6 main/update_tankopedia.py
python3.6 main/update_accounts.py
python3.6 main/update_tanks.py
python3.6 main/calculate_percentiles.py
python3.6 main/calculate_wn8.py
python3.6 main/push_data.py


deactivate
printf "Task complete.\n\n\n"
