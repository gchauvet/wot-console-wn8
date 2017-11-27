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
* First 1000 tanks for each tank id stored in the database without any checks.
* After first 1000 the tank needs to have `tier * 10 + tier * 10 / 2` battles to be added in the database.
* If there are at least 1100 tanks for the tank id:
  * Deleting up to 50 items (if available) with less than `tier * 10 + tier * 10 / 2` number of battles starting with the ones with oldest `last battle time` timestamp.
  * Or deleting 10 items with oldest `last battle time` timestamp.


#### How to run:
The whole repository meant to be run as a cron job once a day, although manual use is also okay.
* python3.6, pip3 and unix shell required.
* `setup.sh` to setup including setting up venv.
* `run.sh` to run from created venv.
