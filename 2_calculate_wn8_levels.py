import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


#Loads data from SQL. Settings inside.
def load_data_from_sql(tank_tier, tank_class, tankopedia):
    tank_tiers = [tank_tier] if tank_tier != 'all' else [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tank_classes = [tank_class] if tank_class != 'all' else ['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG']
    tank_ids = [key for key, value in tankopedia.items() if value['tier'] in tank_tiers and value['type'] in tank_classes]

    conn = sqlite3.connect('data/sqlite.db')
    columns = ['tank_id', 'damage_dealt', 'spotted', 'frags', 'dropped_capture_points', 'wins', 'battles']
    query = "SELECT {} FROM tanks WHERE tank_id IN ({})".format(', '.join(columns), ', '.join(tank_ids))
    df = pd.read_sql(query, conn)

    df['damage_dealt'] = df['damage_dealt'] / df['battles']
    df['spotted'] = df['spotted'] / df['battles']
    df['frags'] = df['frags'] / df['battles']
    df['dropped_capture_points'] = df['dropped_capture_points'] / df['battles']
    df['wins'] = df['wins'] / df['battles'] * 100

    if tank_tier != 'all':
        min_battles = tank_tier * 10 + (tank_tier * 10 / 2)
    else:
        min_battles = 1

    df = df.drop(df[(df.battles < min_battles)].index)

    return({
        'tank_id':                  np.array(df['tank_id']),
        'battles':                  np.array(df['battles']),
        'damage_dealt':             np.array(df['damage_dealt']),
        'dropped_capture_points':   np.array(df['dropped_capture_points']),
        'frags':                    np.array(df['frags']),
        'spotted':                  np.array(df['spotted']),
        'wins':                     np.array(df['wins'])
    })

#WN8 calculators specific for this data.
def calculate_wn8_for_tank(Dmg, Spot, Frag, Def, WinRate, Battles, exp_values):

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
    return(WN8)

#Calculate 2 WN8 arrays side by side.
def calculate_wn8_for_all(data, pc_exp_values, exp_values):
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

#Plotting.
def plot_the_arrays(pc_array, con_array, percentile_settings, path):

    fig = plt.figure()
    ax = fig.add_subplot
    ax = sns.kdeplot(np.array(pc_array), label='PC table')
    ax = sns.kdeplot(np.array(con_array), shade=True, color="r", label='Console table')
    ax.set_xlim([-100, 5000])

    pc_mean     = round(np.mean(pc_array), 2)
    pc_median   = round(np.median(pc_array), 2)
    con_mean    = round(np.mean(con_array), 2)
    con_median  = round(np.median(con_array), 2)
    ax.annotate('PC MEAN:{}'.format(pc_mean), xy=(3000, 0.0005))
    ax.annotate('PC  MED:{}'.format(pc_median), xy=(3000, 0.00045))
    ax.annotate('CONMEAN:{}'.format(con_mean), xy=(3000, 0.0004))
    ax.annotate('CON MED:{}'.format(con_median), xy=(3000, 0.00035))

    plt.title('Tanks: {}'.format(len(con_array)) + ' Settings:' + str(percentile_settings))

    fig.savefig(path)
    plt.close()

#Returns: {tank_id:Int: {key:Str: value:Float}, ...}
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
                'expDamage':  max(round(float(np.percentile(damage,  percentiles['expDamage'])), 2), 0.01),
                'expDef':     max(round(float(np.percentile(defence, percentiles['expDef'])), 2), 0.01),
                'expFrag':    max(round(float(np.percentile(frag,    percentiles['expFrag'])), 2), 0.01),
                'expSpot':    max(round(float(np.percentile(spot,    percentiles['expSpot'])), 2), 0.01),
                'expWinRate': max(round(float(np.percentile(winrate, percentiles['expWinRate'])), 2), 0.01)
            }
    return(output)

#Finding and adjusting percentiles.
def find_percentiles(pc_exp_values, data):

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

    return(percentiles)


with open('references/tankopedia.json') as f:
    tankopedia = json.load(f)

with open('references/wn8pc_v30.json') as f:
    wn8pc = json.load(f)


#Iterating through tiers and calculatin wn8 values.
all_percentiles = {}
wn8console = {}

for tank_type in ['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG']:
    for tank_tier in range(1, 11):

        pc_exp_values = [x for x in wn8pc if x['type'] == tank_type and x['tier'] == tank_tier][0]

        data = load_data_from_sql(tank_tier, tank_type, tankopedia)

        #Skip if less than 2 tanks in tier - class.
        if len(set(data['tank_id'])) < 2:
            continue

        percentiles = find_percentiles(pc_exp_values, data)

        #Not enough values for any of the tanks.
        if percentiles is None:
            continue

        exp_values = get_exp_values(percentiles, data)

        pc_array, con_array = calculate_wn8_for_all(data, pc_exp_values, exp_values)
        plot_the_arrays(pc_array, con_array, percentiles, 'wn8results/{t}{c}.png'.format(t=tank_tier, c=tank_type))

        wn8console.update(exp_values)
        all_percentiles[str(tank_tier) + tank_type] = percentiles


#Saving.
with open('results/wn8console.json', 'w') as f:
    json.dump(wn8console, f)
with open('results/percentiles.json', 'w') as f:
    json.dump(all_percentiles, f)



#Plotting for all.
data = load_data_from_sql('all', 'all', tankopedia)
pc_array, con_array = calculate_wn8_for_all(data, pc_exp_values, exp_values)
plot_the_arrays(pc_array, con_array, 'Not applicable', 'wn8results/all_tanks.png')
