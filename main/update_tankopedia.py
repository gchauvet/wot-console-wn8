from . import wgapi
from .database import t_tankopedia as db_tp


#Update changed and add new tankopedia tanks.


def main():

    #Get new and old tankopedias.
    old_tankopedia = db_tp.get_tankopedia()
    new_tankopedia = wgapi.get_tankopedia()
    if not new_tankopedia:
        print('WARNING: Cant download tankopedia from WG.')
        return


    #Extract keys, getting new and changed tank ids.
    new_keys, old_keys = set(new_tankopedia.keys()), set(old_tankopedia.keys())
    tanks_to_update = []


    #Adding new tanks.
    for tank_id in new_keys - old_keys:
        tank = new_tankopedia.get(tank_id)
        if tank:
            tanks_to_update.append(tank)


    #Adding updated tanks.
    for tank_id in old_keys:
        old_tank = old_tankopedia.get(tank_id)
        new_tank = new_tankopedia.get(tank_id)
        if new_tank and old_tank != new_tank:
            tanks_to_update.append(new_tank)


    #If empty.
    if not tanks_to_update:
        print('SUCCESS: Tankopedia updated: no changes.')
        return


    #Insert.
    db_tp.put(tanks_to_update)


    #Feedback.
    print(f'SUCCESS: Tankopedia updated: {len(tanks_to_update)} tanks.')
    for tank in tanks_to_update:
        print('INFO:', ' '.join([
            'ID:{}'.format(tank['tank_id']),
            'TIER:{}'.format(tank['tier']),
            'TYPE:{}'.format(tank['type']),
            'NATION:{}'.format(tank['nation']),
            'NAME:{}'.format(tank['name']),
            'PREMIUM:{}'.format(tank['is_premium'])
        ]))


if __name__ == '__main__':
    main()
