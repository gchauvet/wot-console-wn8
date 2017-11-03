import requests
import json
import time


#Get full tankopedia.
def get_tankopedia(app_id):
    #Returns: {tank_id:str{...tank_info...}}

    fields = '%2C+'.join(['name', 'short_name', 'nation', 'is_premium', 'tier', 'type', 'tank_id'])
    url = f'https://api-xbox-console.worldoftanks.com/wotx/encyclopedia/vehicles/?application_id={app_id}&fields=' + fields

    attempts, max_attempts = 0, 3
    while attempts < max_attempts:
        try:
            resp = requests.get(url, timeout=30).json()
            status = resp.get('status')
            count = resp.get('meta', {}).get('count')
            data = resp.get('data')
            assert status == 'ok'
            assert len(data) == count
            print('Tankopedia downloaded from WG')
            break
        except (AssertionError, requests.exceptions.Timeout):
            data = None
            attempts += 1

    return data


#Downloading account ids from WGAPI.
def download_accounts(app_id):

    print('Started downloading accounts.')

    #Assembling url. 7 days rating type.
    params = {
        'application_id': app_id,
        'type': '7',
        'rank_field': 'battles_count',
        'fields': '%2C+'.join(['account_id', 'platform']),
        'limit': '1000'
    }
    params_str = '&'.join([f'{key}={val}' for key, val in params.items()])
    url = f'https://api-xbox-console.worldoftanks.com/wotx/ratings/top/?{params_str}&page_no='

    #Initial variables.
    page_no, error_counter = 0, 0
    all_accounts = []

    #Run until hits last page.
    last_page = False
    while not last_page:
        start_time = time.time()
        page_no += 1

        #Making request.
        try:
            resp = requests.get(url + str(page_no), timeout=20).json()
            assert resp.get('status') == 'ok'
            count = resp.get('meta', {}).get('count')
            data = resp.get('data')
            assert len(data) == count

        except Exception as e:
            print('Error:', e)
            error_counter += 1
            #Stop if too many errors.
            if error_counter > 20:
                print('Error: Stopped getting ids because of too many errors.')
                break

        else:
            #Add data.
            all_accounts += data
            #Feedback.
            if page_no % 20 == 0:
                print(f'Downloaded {page_no}k ids')
            #Last page must have less items than requested.
            if len(data) < 1000:
                last_page = True
                print('Finished downloading accounts.')
                break

        finally:
            #Waiting if running too fast.
            if time.time() < start_time + 0.1:
                time.sleep(0.1)

    return all_accounts


#Get player data for one player.
def get_player_data(account_id, server, app_id):

    url = f'https://api-{server}-console.worldoftanks.com/wotx/tanks/stats/?application_id={app_id}&account_id={account_id}'

    try:
        resp = requests.get(url, timeout=25).json()
    except requests.exceptions.Timeout:
        return('error', 'timeout', None)
    except json.decoder.JSONDecodeError:
        return('error', 'cant decode json', None)
    except Exception as e:
        return('error', str(e), None)

    #Getting variables.
    status = resp.get('status')
    message = resp.get('error', {}).get('message')
    data = resp.get('data', {}).get(str(account_id), [])

    #Error.
    if status != 'ok':
        return(status, message, None)

    #Extracting.
    output = []
    for tank in data:
        temp_dict = tank['all']
        temp_dict['account_id']       = tank['account_id']
        temp_dict['battle_life_time'] = tank['battle_life_time']
        temp_dict['last_battle_time'] = tank['last_battle_time']
        temp_dict['mark_of_mastery']  = tank['mark_of_mastery']
        temp_dict['max_frags']        = tank['max_frags']
        temp_dict['max_xp']           = tank['max_xp']
        temp_dict['tank_id']          = tank['tank_id']
        temp_dict['trees_cut']        = tank['trees_cut']
        temp_dict['server']           = server
        output.append(temp_dict)
    return(status, message, output)
