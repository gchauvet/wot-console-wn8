import sqlite3


from .conn import conn, cur


#Functions for WN8 table.


def replace_all(exp_values):
    #Remove all expected values and put new ones.

    cur.execute('DELETE FROM wn8;')
    for tank_id, val in exp_values.items():
        cur.execute('''
            INSERT INTO wn8 (tank_id, expFrag, expDamage, expSpot, expDef, expWinRate)
            VALUES (?, ?, ?, ?, ?, ?);
        ''', (tank_id, val['expFrag'], val['expDamage'], val['expSpot'], val['expDef'], val['expWinRate']))
    conn.commit()
