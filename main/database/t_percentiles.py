import sqlite3
import pickle
import time


from .conn import conn, cur


#Functions for percentiles, percentiles_generic tables.


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
