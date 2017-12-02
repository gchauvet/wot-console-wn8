import time
import numpy as np


from .database.t_tankopedia import get_tankopedia
from .database.t_tanks import get_dataframe
from .database import t_history as db


#Main routine to calculate medians and log them for historical reference.


def main():

    #Current timestamp.
    start_time = int(time.time())


    #Define columns needed.
    columns = [
        'battles', 'last_battle_time',
        'battle_life_time', 'capture_points', 'damage_assisted_radio',
        'damage_dealt', 'damage_received', 'direct_hits_received',
        'frags', 'hits', 'losses', 'piercings', 'piercings_received',
        'shots', 'spotted', 'survived_battles', 'wins', 'xp'
    ]


    #Items that need to be divided by battles.
    ratio_names = columns[2::]


    #Iterate though every tank.
    rows = []
    for tank in get_tankopedia().values():

        tank_id, tier = tank['tank_id'], tank['tier']
        min_battles = tier * 10 + tier * 10 / 2
        df = get_dataframe(tank_ids=[tank_id], columns=columns, min_battles=min_battles)

        #Skip if too little tanks.
        if len(df) < 100:
            continue

        #Calculations.
        df['last_battle_time'] = time.time() - df['last_battle_time']
        for name in ratio_names:
            df[name] = df[name] / df['battles']
        df.drop(columns=['battles'], inplace=True)
        df = df.agg('median').round(2)

        #Put everything into row.
        row = {
            'tank_id':          tank_id,
            'created_at':       start_time,
            'last_battle_time': df['last_battle_time']
        }
        for name in ratio_names:
            row[name] = df[name]
        rows.append(row)


    #Generating 'popularity_index' & updating rows.
    recency_arr = [x['last_battle_time'] for x in rows]
    percentiles = np.percentile(recency_arr, [x / 10 for x in range(0, 1001)])
    for row in rows:
        value = row['last_battle_time']
        for index, perc in enumerate(percentiles):

            #Skip if value is bigger than current percentile value.
            if value > perc and index < 1000:
                continue

            #Previous or current index.
            x = index - 1 if value < perc and index > 0 else index

            #Divide by 10 to get percent with two decimals. + Invert
            x = abs(100 - x / 10)

            #Add inverted value. (bigger = more popular)
            row.update({'popularity_index': round(x, 2)})
            break


    #Insert.
    db.put(rows)


    #Feedback.
    took_time = time.time() - start_time
    print(f'SUCCESS: History updated. Took: {took_time:.02f} s.')


if __name__ == '__main__':
    main()
