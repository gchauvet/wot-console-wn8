import time
import numpy as np


from .database.t_tankopedia import get_distinct_tankids, get_tiertype_tankids
from .database.t_tanks import get_percentiles_data as get_data
from .database import t_percentiles as db


#Main routine to calculate percentiles and generic percentiles.


def calculate_percentiles(headers, data):
    #Calculate percentiles dictionary from the data.

    #Return nothing if not enough values.
    if len(data) < 1000:
        return(None)

    output = {}

    #Create mapping based on header indexes.
    mapping = {}
    for index, header in enumerate(headers):
        mapping[header] = index

    #Get battles array.
    i = mapping['battles']
    battles_arr = np.array([x[i] for x in data])

    #Number / battles -> INTEGER
    for header in ["battle_life_time", "damage_dealt", "damage_received", "xp"]:
        i = mapping[header]
        arr = np.array([x[i] for x in data]) / battles_arr
        output[header] = np.percentile(arr, range(0, 101)).round(decimals=0).astype(int).tolist()

    #Number * 100 / battles -> FLOAT 2D
    for header in ["wins", "survived_battles", "losses"]:
        i = mapping[header]
        arr = np.array([x[i] for x in data]) * 100 / battles_arr
        output[header] = np.percentile(arr, range(0, 101)).round(decimals=2).tolist()

    #Number -> INTEGER
    for header in ["max_frags", "max_xp", "mark_of_mastery"]:
        i = mapping[header]
        arr = np.array([x[i] for x in data])
        output[header] = np.percentile(arr, range(0, 101)).astype(int).tolist()

    #Number / battles -> FLOAT 2D
    for header in [
        "capture_points", "damage_assisted_radio", "damage_assisted_track", "direct_hits_received",
        "no_damage_direct_hits_received", "dropped_capture_points", "explosion_hits", "explosion_hits_received",
        "frags", "hits", "trees_cut", "piercings", "piercings_received", "shots", "spotted"
    ]:
        i = mapping[header]
        arr = np.array([x[i] for x in data]) / battles_arr
        output[header] = np.percentile(arr, range(0, 101)).round(decimals=2).tolist()

    #Accuracy.
    hits_index, shots_index = mapping['hits'], mapping['shots']
    arr = []
    for row in data:
        number = row[hits_index] / row[shots_index] * 100 if row[shots_index] > 0 else 0.0
        arr.append(number)
    output['accuracy'] = np.percentile(arr, range(0, 101)).round(decimals=2).tolist()

    return output


def main():

    #Calculate percentiles for each tank_id.
    start = time.time()
    for tank_id in get_distinct_tankids():
        data = calculate_percentiles(*get_data([tank_id]))
        if data:
            db.update_percentiles(data, tank_id)
    db.conn.commit()
    print('SUCCESS: Percentiles calculated. Took {} s.'.format(int(time.time() - start)))


    #Calculate percentiles for every class-tier.
    start = time.time()
    for tank_type in ['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG']:
        for tank_tier in range(1, 11):
            tank_ids = get_tiertype_tankids(tank_tier, tank_type)
            data = calculate_percentiles(*get_data(tank_ids))
            #Data is None if not enough tanks.
            db.update_percentiles_generic(data, tank_tier, tank_type)
    db.conn.commit()
    print('SUCCESS: Generic percentiles calculated. Took {} s.'.format(int(time.time() - start)))


if __name__ == '__main__':
    main()
