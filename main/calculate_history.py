import time
import numpy


from .database.t_tankopedia import get_tankopedia
from .database.t_tanks import get_dataframe
from .database import t_history as db


#Main routine to calculate medians and log them for historical reference.


def main():

    #Current timestamp.
    now = int(time.time())


    #Define columns needed.
    columns = [
        'battles', 'last_battle_time',
        'battle_life_time', 'capture_points', 'damage_assisted_radio',
        'damage_dealt', 'damage_received', 'direct_hits_received',
        'frags', 'hits', 'losses', 'piercings', 'piercings_received',
        'shots', 'spotted', 'survived_battles', 'wins', 'xp'
    ]
    to_remove = columns[0:2]
    ratios = columns[2::]


    #Iterate though every tank.
    rows = []
    for tank in get_tankopedia().values():

        tank_id, tier = tank['tank_id'], tank['tier']
        min_battles = tier * 10 + tier * 10 / 2
        df = get_dataframe(tank_ids=[tank_id], columns=columns, min_battles=min_battles)


        #Skip if not enough tanks.
        if len(df) < 1000:
            continue


        #Calculations.
        df['recency'] = int(time.time()) - df['last_battle_time']
        for col_name in ratios:
            df[col_name] = df[col_name] / df['battles']
        for col_name in to_remove:
            del df[col_name]
        df = df.agg('median').round(2)


        #Create a row.
        rows.append({
            'tank_id':               tank_id,
            'created_at':            now,
            'recency':               int(df['recency']),
            'battle_life_time':      df['battle_life_time'],
            'capture_points':        df['capture_points'],
            'damage_assisted_radio': df['damage_assisted_radio'],
            'damage_dealt':          df['damage_dealt'],
            'damage_received':       df['damage_received'],
            'direct_hits_received':  df['direct_hits_received'],
            'frags':                 df['frags'],
            'hits':                  df['hits'],
            'losses':                df['losses'],
            'piercings':             df['piercings'],
            'piercings_received':    df['piercings_received'],
            'shots':                 df['shots'],
            'spotted':               df['spotted'],
            'survived_battles':      df['survived_battles'],
            'wins':                  df['wins'],
            'xp':                    df['xp']
        })

    db.put(rows)


if __name__ == '__main__':
    main()
