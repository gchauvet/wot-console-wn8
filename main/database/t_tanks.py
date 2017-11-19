import sqlite3
import pandas as pd

from .conn import conn, cur


#Functions for tanks table.


def get_percentiles_data(tank_ids):
    columns = [
        'battle_life_time', 'battles', 'capture_points', 'damage_assisted_radio',
        'damage_assisted_track', 'damage_dealt', 'damage_received', 'direct_hits_received',
        'dropped_capture_points', 'explosion_hits', 'explosion_hits_received', 'frags',
        'hits', 'losses', 'mark_of_mastery', 'max_frags',
        'max_xp', 'no_damage_direct_hits_received', 'piercings', 'piercings_received',
        'shots', 'spotted', 'survived_battles', 'trees_cut',
        'wins', 'xp'
    ]

    tank_ids_str = ', '.join([str(x) for x in tank_ids])
    columns_str = ', '.join(columns)

    data = cur.execute(f'''
        SELECT {columns_str} FROM tanks WHERE tank_id IN ({tank_ids_str});
    ''').fetchall()

    return columns, data


def get_dataframe(tank_ids, columns, min_battles=1):

    tank_ids_str = ', '.join([str(x) for x in tank_ids])
    columns_str = ', '.join(columns)

    return pd.read_sql(f'''
        SELECT {columns_str} FROM tanks
        WHERE tank_id IN ({tank_ids_str}) AND battles >= {min_battles}
    ''', conn)


def insert_tank(tank_data):
    #Process player and insert tanks into "tanks" table.
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
    cur.execute('''
        SELECT COUNT(*) FROM tanks
        WHERE tank_id = ? AND battles < ?;
    ''', (tank_id, min_battles))
    count = cur.fetchone()[0]

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
    else:
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
