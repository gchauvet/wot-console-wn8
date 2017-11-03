import modules.wgapi as wgapi
import modules.database as db
from secret import app_id


# Update changed and add new tankopedia tanks.


def main():

    print('Updating tankopedia...')

    #Download tankopedia from WG.
    new_tankopedia = wgapi.get_tankopedia(app_id)
    if not new_tankopedia:
        print('Couldnt download tankopedia.')
        return


    #Get tankopedia from database.
    old_tankopedia = db.get_tankopedia()


    #Getting new ids that are not in the database.
    new_keys, old_keys = set(new_tankopedia.keys()), set(old_tankopedia.keys())


    #Getting ids for new and changed tanks.
    new_tank_ids = list(new_keys - old_keys)
    changed_tank_ids = []
    for tank_id in old_keys:
        if old_tankopedia.get(tank_id) != new_tankopedia.get(tank_id):
            changed_tank_ids.append(tank_id)


    #Adding tanks into a list.
    tanks_to_update = []
    for tank_id in new_tank_ids + changed_tank_ids:
        tank_dict = new_tankopedia.get(tank_id)
        if tank_dict:
            tanks_to_update.append(tank_dict)


    #If empty.
    if not tanks_to_update:
        print('Tankopedia updated: no changes.')
        return


    #Insert.
    db.put_tanks_into_tankopedia(tanks_to_update)


    #Feedback.
    print('Tankopedia updated:')
    for tank in tanks_to_update:
        print(' '.join([
            'ID:{}'.format(tank['tank_id']),
            'TIER:{}'.format(tank['tier']),
            'TYPE:{}'.format(tank['type']),
            'NATION:{}'.format(tank['nation']),
            'NAME:{}'.format(tank['name']),
            'PREMIUM:{}'.format(tank['is_premium'])
        ]))


if __name__ == '__main__':
    main()
