import sqlite3
import pickle
import time
import pandas as pd


#Global connection variables.
conn = sqlite3.connect('sqlite.db')
cur = conn.cursor()


#Tankopedia.
def get_tankopedia():
    #Return tankopedia as dictionary of dictionaries.
    #Keys are strings of numbers representing tank ids.
    #Output: {"111": {...}, ...}

    output = {}
    cur.execute('SELECT tank_id, name, short_name, nation, is_premium, tier, type FROM tankopedia')
    for row in cur:
        output[str(row[0])] = {
            "tank_id":      row[0],
            "name":         row[1],
            "short_name":   row[2],
            "nation":       row[3],
            "is_premium":   True if row[4] == 1 else False,
            "tier":         row[5],
            "type":         row[6]
        }

    return output
def put_tanks_into_tankopedia(tank_list):
    #Input: [{...}, {...}, ...]

    for tank in tank_list:

        now = int(time.time())
        found = cur.execute('SELECT 1 FROM tankopedia WHERE tank_id = ?', (tank['tank_id'],)).fetchone()

        if not found:
            query = '''
                INSERT INTO tankopedia (tank_id, updated_at, name, short_name, nation, is_premium, tier, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            '''
            cur.execute(query, (
                tank['tank_id'],
                now,
                tank['name'],
                tank['short_name'],
                tank['nation'],
                1 if tank['is_premium'] == True else 0,
                tank['tier'],
                tank['type']
            ))
        else:
            query = '''
                UPDATE tankopedia
                SET updated_at = ?, name = ?, short_name = ?, nation = ?, is_premium = ?, tier = ?, type = ?
                WHERE tank_id = ?;
            '''
            cur.execute(query, (
                now,
                tank['name'],
                tank['short_name'],
                tank['nation'],
                1 if tank['is_premium'] == True else 0,
                tank['tier'],
                tank['type'],
                tank['tank_id']
            ))

    conn.commit()


#Process player and insert tanks into "tanks" table.
def insert_tank(tank_data):
    x = tank_data

    #Checking if the tank is already in the database for the same user.
    last_battle_time = cur.execute('''
        SELECT last_battle_time FROM tanks
        WHERE tank_id = ? AND account_id = ? AND server = ?;
    ''', (x['tank_id'], x['account_id'], x['server'])).fetchone()

    #If found.
    if last_battle_time:
        last_battle_time = last_battle_time[0]

        #Do nothing if the data contains the same timestamp.
        if last_battle_time == x['last_battle_time']:
            return

        #Delete if data contains newer timestamp.
        cur.execute('''
            DELETE FROM tanks
            WHERE tank_id = ? AND last_battle_time = ? AND account_id = ? AND server = ?;
        ''', (x['tank_id'], last_battle_time, x['account_id'], x['server']))

    query = '''
        INSERT INTO tanks (
            tank_id,                        last_battle_time,               account_id,
            server,                         battle_life_time,               battles,
            capture_points,                 damage_assisted_radio,          damage_assisted_track,
            damage_dealt,                   damage_received,                direct_hits_received,
            dropped_capture_points,         explosion_hits,                 explosion_hits_received,
            frags,                          hits,                           losses,
            mark_of_mastery,                max_frags,                      max_xp,
            no_damage_direct_hits_received, piercings,                      piercings_received,
            shots,                          spotted,                        survived_battles,
            trees_cut,                      wins,                           xp )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    '''

    values = (
        x['tank_id'],                        x['last_battle_time'],      x['account_id'],
        x['server'],                         x['battle_life_time'],      x['battles'],
        x['capture_points'],                 x['damage_assisted_radio'], x['damage_assisted_track'],
        x['damage_dealt'],                   x['damage_received'],       x['direct_hits_received'],
        x['dropped_capture_points'],         x['explosion_hits'],        x['explosion_hits_received'],
        x['frags'],                          x['hits'],                  x['losses'],
        x['mark_of_mastery'],                x['max_frags'],             x['max_xp'],
        x['no_damage_direct_hits_received'], x['piercings'],             x['piercings_received'],
        x['shots'],                          x['spotted'],               x['survived_battles'],
        x['trees_cut'],                      x['wins'],                  x['xp']
    )

    cur.execute(query, values)
def cleanup_space(tank_id, min_battles):

    #Getting count of tanks with battles less than minimum.
    count = cur.execute('''
        SELECT COUNT(*) FROM tanks WHERE tank_id = ? AND battles < ?;
    ''', (tank_id, min_battles)).fetchone()[0]

    if count > 0:
        #Deleting oldest 50 with battles less than minimum.
        cur.execute('''
            DELETE FROM tanks
            WHERE tank_id = ? AND account_id IN (
                SELECT account_id FROM tanks
                WHERE tank_id = ? AND battles < ?
                ORDER BY last_battle_time ASC LIMIT 50
            );
        ''', (tank_id, tank_id, min_battles))
        return

    #Deleting oldest 10.
    cur.execute('''
        DELETE FROM tanks
        WHERE tank_id = ? AND last_battle_time IN (
            SELECT last_battle_time FROM tanks
            WHERE tank_id = ?
            ORDER BY last_battle_time ASC LIMIT 10
        );
    ''', (tank_id, tank_id))
def insert_player(player_data, tankopedia):
    for tank_data in player_data:
        tank_id = tank_data['tank_id']

        #Getting count of the tank_id.
        count = cur.execute('SELECT COUNT(account_id) FROM tanks WHERE tank_id = ?', (tank_id,)).fetchone()[0]

        #No min_battles check.
        if count < 1000:
            insert_tank(tank_data)
            continue

        #Calculating min_battles. Skip if tank not in tankopedia.
        tier = tankopedia.get(str(tank_id), {}).get('tier')
        if tier:
            min_battles = tier * 10 + tier * 10 / 2

            #Cleanup if too many.
            if count >= 1100:
                cleanup_space(tank_id, min_battles)

            if tank_data['battles'] >= min_battles:
                insert_tank(tank_data)

    conn.commit()

#Accounts table.
def count_accounts():
    return cur.execute('SELECT COUNT(*) FROM accounts;').fetchone()[0]
def get_all_accounts():
    #Returns all accounts.

    cur.execute('SELECT * FROM accounts;')
    return [{'account_id': row[0], 'platform': row[1]} for row in cur]
def remove_all_accounts():
    cur.execute('DELETE FROM accounts;')
    conn.commit()
def remove_accounts(accounts):
    #Input: [{'account_id': 1223456, 'platform': 'ps4'}, ...]

    tuples = [(row['account_id'], row['platform']) for row in accounts]
    cur.executemany('DELETE FROM accounts WHERE account_id = ? AND server = ?;', tuples)
    conn.commit()
def insert_accounts(accounts):
    #Input: [{'account_id': 1223456, 'platform': 'ps4'}, ...]

    tuples = [(row['account_id'], row['platform']) for row in accounts]
    cur.executemany('INSERT INTO accounts (account_id, server) VALUES (?, ?);', tuples)
    conn.commit()

#Calculations.
def get_tiertype_tankids(tank_tier, tank_type):
    cur.execute('SELECT tank_id FROM tankopedia WHERE tier = ? AND type = ?;', (tank_tier,  tank_type))
    return [x[0] for x in cur]
def get_distinct_tankids():
    cur.execute('SELECT DISTINCT(tank_id) FROM tankopedia;')
    return [x[0] for x in cur]
def get_tanks_data(tank_ids_list):
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

#Percentiles (+ generic) table.
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

#WN8
def get_wn8_arrays(tankopedia, tank_tier='all', tank_type='all'):
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
def update_wn8_exp_values(exp_values):
    #Remove all expected values and put new ones.

    cur.execute('DELETE FROM wn8;')
    for tank_id, val in exp_values.items():
        cur.execute('''
            INSERT INTO wn8 (tank_id, expFrag, expDamage, expSpot, expDef, expWinRate)
            VALUES (?, ?, ?, ?, ?, ?);
        ''', (tank_id, val['expFrag'], val['expDamage'], val['expSpot'], val['expDef'], val['expWinRate']))
    conn.commit()


#Export data as list of dictionaries
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
