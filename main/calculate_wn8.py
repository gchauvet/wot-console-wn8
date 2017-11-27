import time
import numpy as np


from .database.t_tanks import get_dataframe
from .database.t_tankopedia import get_tankopedia
from .database import t_wn8 as db
from .wn8pc import wn8pc


#Main routine to calculate WN8 expected values.

def calculate_exp_values(percentiles, df):

    output = {}

    for tank_id in df['tank_id'].unique():

        #Referencing a slice.
        d = df[df['tank_id'] == tank_id]

        #Need at least 100 rows for tank_id.
        if d['tank_id'].count() < 100:
            continue

        output[int(tank_id)] = {
            'tank_id':    int(tank_id),
            'expDamage':  max(float(np.percentile(d['damage_dealt'],           percentiles['expDamage']).round(2)),  0.01),
            'expDef':     max(float(np.percentile(d['dropped_capture_points'], percentiles['expDef']).round(2)),     0.01),
            'expFrag':    max(float(np.percentile(d['frags'],                  percentiles['expFrag']).round(2)),    0.01),
            'expSpot':    max(float(np.percentile(d['spotted'],                percentiles['expSpot']).round(2)),    0.01),
            'expWinRate': max(float(np.percentile(d['wins'],                   percentiles['expWinRate']).round(2)), 0.01)
        }

    return output


def find_percentiles(pc_exp_values, df):
    #Find percentiles for values that match pc_exp_values.

    tank_ids = df['tank_id'].unique().tolist()
    percentiles = {'expDamage': 50, 'expDef': 50, 'expFrag': 50, 'expSpot': 50, 'expWinRate': 50}
    previous_change = ['+' for i in range(5)]
    found = [False for i in range(5)]

    while not all(found):
        exp_values = calculate_exp_values(percentiles, df)

        #Not enough data for each tank_id in df.
        if not any(exp_values):
            return

        #Iterating through WN8 values.
        for i, stat_type in enumerate(['expDamage', 'expDef', 'expFrag', 'expSpot', 'expWinRate']):

            if found[i] == True:
                continue

            #Getting the median of exp_values for stat_type.
            pc = pc_exp_values[stat_type]
            con = np.median([x[stat_type] for x in exp_values.values()]).round(2)

            #Checking conditions.
            if pc == con:
                found[i] = True
            elif pc > con:
                percentiles[stat_type] += 1
                if previous_change[i] == '-':
                    found[i] = True
                #99 is the max.
                if percentiles[stat_type] == 99:
                    found[i] = True
            elif pc < con:
                percentiles[stat_type] -= 1
                previous_change[i] = '-'

    return percentiles


def calculate_wn8_for_tank(Dmg, Spot, Frag, Def, WinRate, Battles, exp_values):
    #Calculate WN8 for single tank with specified WN8 exp_values.

    #step 0 - assigning the variables
    expDmg      = exp_values['expDamage']
    expSpot     = exp_values['expSpot']
    expFrag     = exp_values['expFrag']
    expDef      = exp_values['expDef']
    expWinRate  = exp_values['expWinRate']

    #step 1 (original)
    #rDAMAGE = Dmg       /   Battles     / expDmg
    #rSPOT   = Spot      /   Battles     / expSpot
    #rFRAG   = Frag      /   Battles     / expFrag
    #rDEF    = Def       /   Battles     / expDef
    #rWIN    = WinRate   /   Battles*100 / expWinRate

    #step 1 (omitting division by battles as the data was prepared this way before)
    rDAMAGE = Dmg       / expDmg
    rSPOT   = Spot      / expSpot
    rFRAG   = Frag      / expFrag
    rDEF    = Def       / expDef
    rWIN    = WinRate   / expWinRate

    #step 2
    rWINc    = max(0,                     (rWIN    - 0.71) / (1 - 0.71) )
    rDAMAGEc = max(0,                     (rDAMAGE - 0.22) / (1 - 0.22) )
    rFRAGc   = max(0, min(rDAMAGEc + 0.2, (rFRAG   - 0.12) / (1 - 0.12)))
    rSPOTc   = max(0, min(rDAMAGEc + 0.1, (rSPOT   - 0.38) / (1 - 0.38)))
    rDEFc    = max(0, min(rDAMAGEc + 0.1, (rDEF    - 0.10) / (1 - 0.10)))

    #step 3
    WN8 = 980*rDAMAGEc + 210*rDAMAGEc*rFRAGc + 155*rFRAGc*rSPOTc + 75*rDEFc*rFRAGc + 145*min(1.8,rWINc)

    return WN8


def main():

    #Benchmarking.
    start_time =  time.time()

    #Output: {"tank_id": {"expVal": float, ...}, ...}
    output = {}

    tankopedia = get_tankopedia()

    columns = ['tank_id', 'damage_dealt', 'spotted', 'frags', 'dropped_capture_points', 'wins', 'battles']

    for tank_type in ['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG']:
        for tank_tier in range(1, 11):

            pc_exp_values = [x for x in wn8pc if x['type'] == tank_type and x['tier'] == tank_tier][0]
            tank_ids = [x['tank_id'] for x in tankopedia.values() if x['type'] == tank_type and x['tier'] == tank_tier]
            df = get_dataframe(tank_ids, columns, min_battles=1)

            df['damage_dealt']           = df['damage_dealt']           / df['battles']
            df['spotted']                = df['spotted']                / df['battles']
            df['frags']                  = df['frags']                  / df['battles']
            df['dropped_capture_points'] = df['dropped_capture_points'] / df['battles']
            df['wins']                   = df['wins']                   / df['battles'] * 100

            #Skip if 0 or 1 tank in tier-class. Use generic value instead.
            if df['tank_id'].nunique() <= 1:
                continue

            percentiles = find_percentiles(pc_exp_values, df)

            #Not enough values for any of the tanks.
            if not percentiles:
                continue

            exp_values = calculate_exp_values(percentiles, df)
            output.update(exp_values)

    db.replace_all(output)

    took = int(time.time() - start_time)
    print(f'SUCCESS: Calculated WN8. Took {took} s.')


if __name__ == '__main__':
    main()
