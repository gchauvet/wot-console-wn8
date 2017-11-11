import sqlite3
import pickle
import time


from .conn import conn, cur


#Functions for percentiles, percentiles_generic tables.


def get_tiertype_tankids(tank_tier, tank_type):
    cur.execute('SELECT tank_id FROM tankopedia WHERE tier = ? AND type = ?;', (tank_tier,  tank_type))
    return [x[0] for x in cur]


def get_distinct_tankids():
    cur.execute('SELECT DISTINCT(tank_id) FROM tankopedia;')
    return [x[0] for x in cur]


def get_data(tank_ids_list):
    columns = [
        'battle_life_time', 'battles', 'capture_points', 'damage_assisted_radio',
        'damage_assisted_track', 'damage_dealt', 'damage_received', 'direct_hits_received',
        'dropped_capture_points', 'explosion_hits', 'explosion_hits_received', 'frags',
        'hits', 'losses', 'mark_of_mastery', 'max_frags',
        'max_xp', 'no_damage_direct_hits_received', 'piercings', 'piercings_received',
        'shots', 'spotted', 'survived_battles', 'trees_cut',
        'wins', 'xp'
    ]

    tank_ids = [str(x) for x in tank_ids_list]
    tank_ids_str = ', '.join(tank_ids)
    columns_str = ', '.join(columns)

    data = cur.execute(f'''
        SELECT {columns_str} FROM tanks WHERE tank_id IN ({tank_ids_str});
    ''').fetchall()

    return columns, data


def update_percentiles(data, tank_id):
    #Update percentiles for one tank - no commit.

    found = cur.execute('SELECT 1 FROM percentiles WHERE tank_id = ?;', [tank_id]).fetchone()

    updated_at = int(time.time())

    if not found:
        cur.execute('''
            INSERT INTO percentiles (tank_id, updated_at, data) VALUES (?, ?, ?);
        ''', (tank_id, updated_at, pickle.dumps(data)))
    else:
        cur.execute('''
            UPDATE percentiles SET updated_at = ?, data = ? WHERE tank_id = ?;
        ''', (updated_at, pickle.dumps(data), tank_id))


def update_percentiles_generic(data, tank_tier, tank_type):
    #Update percentiles for one tier-class - no commit.

    found = cur.execute('''
        SELECT 1 FROM percentiles_generic WHERE tier = ? AND type = ?;
    ''', (tank_tier, tank_type)).fetchone()

    updated_at = int(time.time())

    if not found:
        cur.execute('''
            INSERT INTO percentiles_generic (tier, type, updated_at, data) VALUES (?, ?, ?, ?);
        ''', (tank_tier, tank_type, updated_at, pickle.dumps(data)))
    else:
        cur.execute('''
            UPDATE percentiles_generic SET updated_at = ?, data = ? WHERE tier = ? AND type = ?;
        ''', (updated_at, pickle.dumps(data), tank_tier, tank_type))
