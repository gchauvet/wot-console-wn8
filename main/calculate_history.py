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
    cols_to_remove = columns[0:2]
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
        df.drop(columns=cols_to_remove, inplace=True)
        df = df.agg('median').round(2)


        #Put everything into row.
        row = {
            'tank_id':    tank_id,
            'created_at': now,
            'recency':    int(df['recency'])
        }
        for col_name in ratios:
            row[col_name] = df[col_name]
        rows.append(row)

    db.put(rows)


if __name__ == '__main__':
    main()
