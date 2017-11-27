import sqlite3
import pickle


from .conn import conn, cur


#Export data as list of dictionaries.


def export_tankopedia():

    output = []
    cur.execute('SELECT tank_id, name, short_name, nation, is_premium, tier, type FROM tankopedia')
    for row in cur:
        output.append({
            "tank_id":      row[0],
            "name":         row[1],
            "short_name":   row[2],
            "nation":       row[3],
            "is_premium":   True if row[4] == 1 else False,
            "tier":         row[5],
            "type":         row[6]
        })

    return output


def export_percentiles():

    cur.execute('SELECT tank_id, data FROM percentiles;')
    return [{'tank_id': x[0], 'data': pickle.loads(x[1])} for x in cur]


def export_percentiles_generic():

    cur.execute('SELECT tier, type, data FROM percentiles_generic;')
    return [{'tier': x[0], 'type':x[1], 'data': pickle.loads(x[2])} for x in cur]


def export_wn8_exp_values():

    output = []
    cur.execute('SELECT tank_id, expFrag, expDamage, expSpot, expDef, expWinRate FROM wn8;')
    for row in cur:
        output.append({
            'tank_id':    row[0],
            'expFrag':    row[1],
            'expDamage':  row[2],
            'expSpot':    row[3],
            'expDef':     row[4],
            'expWinRate': row[5]
        })

    return output
