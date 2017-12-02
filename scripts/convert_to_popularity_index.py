#This script must be used to convert old 'recency' column into 'popularity' column in 'history' table.
#Recency was using absolute number of seconds since the median time when the last time the tank was played. Median of (int(time.time()) - last_battle_time)
#This must be normalized to allow future increase in data collection. (e.g. collecting more tanks per day)


import sqlite3
import pandas as pd
import numpy as np


conn = sqlite3.connect('sqlite.db')
cur = conn.cursor()


#Validation.
try:
    cur.execute('SELECT 1 FROM history LIMIT 1')
    print('INFO: \'history\' table found.')
except sqlite3.OperationalError:
    print('ERROR: \'history\' table does not exist.')
    quit()


#Validation.
try:
    cur.execute('SELECT recency FROM history LIMIT 1')
    print('INFO: \'recency\' column found.')
except sqlite3.OperationalError:
    print('ERROR: \'recency\' column does not exist in \'history\' table.')
    quit()


cur.execute('''
    CREATE TABLE temp_history (
        tank_id INTEGER,
        created_at INTEGER,
        recency INTEGER,
        battle_life_time REAL,
        capture_points REAL,
        damage_assisted_radio REAL,
        damage_dealt REAL,
        damage_received REAL,
        direct_hits_received REAL,
        frags REAL,
        hits REAL,
        losses REAL,
        piercings REAL,
        piercings_received REAL,
        shots REAL,
        spotted REAL,
        survived_battles REAL,
        wins REAL,
        xp REAL,
        PRIMARY KEY (tank_id, created_at)
);''')
conn.commit()


cur.execute('INSERT INTO temp_history SELECT * FROM history')
conn.commit()


cur.execute('DROP TABLE history')
conn.commit()


cur.execute('''
    CREATE TABLE history (
        tank_id INTEGER,
        created_at INTEGER,
        popularity_index REAL,
        battle_life_time REAL,
        capture_points REAL,
        damage_assisted_radio REAL,
        damage_dealt REAL,
        damage_received REAL,
        direct_hits_received REAL,
        frags REAL,
        hits REAL,
        losses REAL,
        piercings REAL,
        piercings_received REAL,
        shots REAL,
        spotted REAL,
        survived_battles REAL,
        wins REAL,
        xp REAL,
        PRIMARY KEY (tank_id, created_at)
);''')
conn.commit()


cur.execute('''
    INSERT INTO history
    SELECT
        tank_id,
        created_at,
        recency * 1.0 AS popularity_index,
        battle_life_time,
        capture_points,
        damage_assisted_radio,
        damage_dealt,
        damage_received,
        direct_hits_received,
        frags,
        hits,
        losses,
        piercings,
        piercings_received,
        shots,
        spotted,
        survived_battles,
        wins,
        xp
    FROM temp_history
''')
conn.commit()


cur.execute('DROP TABLE temp_history')
conn.commit()


cur.execute('SELECT DISTINCT(created_at) FROM history')
timestamps = [x[0] for x in cur]


for timestamp in timestamps:
    cur.execute('SELECT tank_id, popularity_index FROM history WHERE created_at = ?', [timestamp])
    tanks = {}
    for row in cur:
        tank_id, recency = row[0], row[1]
        tanks[tank_id] = recency

    recency_arr = list(tanks.values())
    percentiles = []
    for i in range(0, 1001):
        x = float(np.percentile(recency_arr, i / 10))
        percentiles.append(x)

    for tank_id, value in tanks.items():
        for p, perc in enumerate(percentiles):

            if value > perc and p < 1000:
                continue

            else:
                if value < perc and p > 0:
                    x = (p - 1) / 10
                else:
                    x = p / 10

                #Invert.
                x = abs(100 - x)

                cur.execute('''
                    UPDATE history
                    SET popularity_index = ?
                    WHERE tank_id = ? AND created_at = ?
                ''', [x, tank_id, timestamp])

                break
conn.commit()

cur.execute('VACUUM')

print('Done')
