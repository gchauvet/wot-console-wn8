# wot-console-wn8

#### WN8 calculation principles:
With PC community moving towards WN8 v30 expected values, the task of generating Console values became much easier. All that has to be done to get the Console values is to normalize all the tanks in the game across 50 categories (tier-type combinations). This gives underperforming tanks lower expected values and better performing tanks - higher while keeping overall median of the tier-type at the level defined with WN8 PC v30.


#### Update:
From OCT 2017 merged with `wot-console-dataminer` for additional features.
* Fail-proof tankopedia updates.
* WoT Console player data collection (both xbox & ps4).
* Percentiles & generic percentiles calculation.
* WN8 Console-specific expected values calculation (based on WN8 PC v30).


#### Data collection methodology:
* First 1000 tanks for each tank_id are collected without any checks. 
* Set minumum number of battles as `tier * 10 + tier * 10 / 2` for each tank_id with more than 1000 tanks in the database.
* If the number of tanks with the same tank_id hit 1100:
  * Deleting up to 50 tanks with less than `tier * 10 + tier * 10 / 2` battles starting with oldest `last battle time` timestamp.
  * Or deleting 10 items with oldest `last battle time` timestamp.


#### How to run on Linux/Mac:
The whole repository meant to be run as a cron job once a day, although manual use is also okay.
* install python3.6
* setup `setup.sh`
  * python virtual environment setup.
  * creating `main/secret.py` with WG app_id & hosts which should receive the data.
  * initializing SQLite databese inside project directory.
* run `run.sh`
  * switch to venv and run `run.py`
