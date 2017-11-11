import time
import numpy as np


from .database.t_tankopedia import get_tankopedia
from .database import t_wn8 as db
from .wn8pc import wn8pc


#Main routine to calculate WN8 expected values.


def find_percentiles(pc_exp_values, data):
    #Find percentiles for values that match pc_exp_values.

    tank_ids = list(set(data['tank_id']))
    percentiles = {'expDamage': 50, 'expDef': 50, 'expFrag': 50, 'expSpot': 50, 'expWinRate': 50}
    previous_change = ['+' for i in range(5)]
    found = [False for i in range(5)]

    while all(found) == False:

        exp_values = get_exp_values(percentiles, data)

        if len(exp_values) == 0:
            return(None)

        #Iterating through WN8 values.
        for i, stat_type in enumerate(['expDamage', 'expDef', 'expFrag', 'expSpot', 'expWinRate']):

            if found[i] == True:
                continue

            #Getting the median.
            pc = pc_exp_values[stat_type]
            con_array = []
            for tank_id in tank_ids:
                if exp_values.get(tank_id):
                    con_array.append(exp_values[tank_id][stat_type])
            con = round(np.median(con_array), 2)

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


def get_exp_values(percentiles, data):

    output = {}

    for tank_id in set(data['tank_id']):

        damage, defence, frag, spot, winrate = ([] for i in range(5))

        for i in range(len(data['tank_id'])):

            if tank_id == data['tank_id'][i]:
                damage.append(data['damage_dealt'][i])
                defence.append(data['dropped_capture_points'][i])
                frag.append(data['frags'][i])
                spot.append(data['spotted'][i])
                winrate.append(data['wins'][i])

        #At least 100 values.
        if len(damage) >= 100:
            output[int(tank_id)] = {
                'tank_id':    int(tank_id),
                'expDamage':  max(round(float(np.percentile(damage,  percentiles['expDamage'])),  2), 0.01),
                'expDef':     max(round(float(np.percentile(defence, percentiles['expDef'])),     2), 0.01),
                'expFrag':    max(round(float(np.percentile(frag,    percentiles['expFrag'])),    2), 0.01),
                'expSpot':    max(round(float(np.percentile(spot,    percentiles['expSpot'])),    2), 0.01),
                'expWinRate': max(round(float(np.percentile(winrate, percentiles['expWinRate'])), 2), 0.01)
            }

    return output


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


def calculate_wn8_scores(data, pc_exp_values, exp_values):
    tank_id =                data['tank_id']
    battles =                data['battles']
    damage_dealt =           data['damage_dealt']
    dropped_capture_points = data['dropped_capture_points']
    frags =                  data['frags']
    spotted =                data['spotted']
    wins =                   data['wins']

    pc_output = []
    con_output = []

    for i in range(len(tank_id)):
        if exp_values.get(tank_id[i]):

            Dmg, Spot, Frag, Def, WinRate, Battles = damage_dealt[i], spotted[i], frags[i], dropped_capture_points[i], wins[i], battles[i]

            pc_score = calculate_wn8_for_tank(Dmg, Spot, Frag, Def, WinRate, Battles, pc_exp_values)
            con_score = calculate_wn8_for_tank(Dmg, Spot, Frag, Def, WinRate, Battles, exp_values[tank_id[i]])

            pc_output.append(pc_score)
            con_output.append(con_score)

    return(pc_output, con_output)


def main():

    tankopedia = get_tankopedia()

    output, start_time = {}, time.time()

    for tank_type in ['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG']:
        for tank_tier in range(1, 11):

            pc_exp_values = [x for x in wn8pc if x['type'] == tank_type and x['tier'] == tank_tier][0]
            data = db.get_data(tankopedia, tank_tier, tank_type)

            #Skip if less than 2 tanks in tier-class.
            if len(set(data['tank_id'])) < 2:
                continue

            percentiles = find_percentiles(pc_exp_values, data)

            #Not enough values for any of the tanks.
            if percentiles is None:
                continue

            exp_values = get_exp_values(percentiles, data)
            pc_array, con_array = calculate_wn8_scores(data, pc_exp_values, exp_values)
            output.update(exp_values)

    db.replace_all(output)

    took = int(time.time() - start_time)
    print(f'SUCCESS: Calculated WN8. Took {took} s.')


if __name__ == '__main__':
    main()
