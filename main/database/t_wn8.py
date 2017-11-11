import sqlite3
import pandas as pd

from .conn import conn, cur


#Functions for WN8 table.


def get_data(tankopedia, tank_tier='all', tank_type='all'):
    #Get dictionary of numpy arrays for WN8 calculation filtered by tier and type.

    #Get tank ids.
    tank_tiers = [tank_tier] if tank_tier != 'all' else list(range(1, 11))
    tank_types = [tank_type] if tank_type != 'all' else ['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG']
    tank_ids = [key for key, val in tankopedia.items() if val['tier'] in tank_tiers and val['type'] in tank_types]

    #Query into pandas dataframe.
    columns_str = ', '.join(['tank_id', 'damage_dealt', 'spotted', 'frags', 'dropped_capture_points', 'wins', 'battles'])
    tank_ids_str = ', '.join(tank_ids)
    df = pd.read_sql(f'SELECT {columns_str} FROM tanks WHERE tank_id IN ({tank_ids_str});', conn)

    #Calculations.
    df['damage_dealt']           = df['damage_dealt']           / df['battles']
    df['spotted']                = df['spotted']                / df['battles']
    df['frags']                  = df['frags']                  / df['battles']
    df['dropped_capture_points'] = df['dropped_capture_points'] / df['battles']
    df['wins']                   = df['wins']                   / df['battles'] * 100

    #Return as numpy arrays.
    return({
        'tank_id':                df['tank_id'].values,
        'battles':                df['battles'].values,
        'damage_dealt':           df['damage_dealt'].values,
        'dropped_capture_points': df['dropped_capture_points'].values,
        'frags':                  df['frags'].values,
        'spotted':                df['spotted'].values,
        'wins':                   df['wins'].values
    })


def replace_all(exp_values):
    #Remove all expected values and put new ones.

    cur.execute('DELETE FROM wn8;')
    for tank_id, val in exp_values.items():
        cur.execute('''
            INSERT INTO wn8 (tank_id, expFrag, expDamage, expSpot, expDef, expWinRate)
            VALUES (?, ?, ?, ?, ?, ?);
        ''', (tank_id, val['expFrag'], val['expDamage'], val['expSpot'], val['expDef'], val['expWinRate']))
    conn.commit()
