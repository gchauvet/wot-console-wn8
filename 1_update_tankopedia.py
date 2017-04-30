import requests
import json

def download_tankopedia():
    fields = '%2C+'.join(['name', 'short_name', 'nation', 'is_premium', 'tier', 'type', 'tank_id'])
    url = 'https://api-xbox-console.worldoftanks.com/wotx/encyclopedia/vehicles/?application_id=demo&fields=' + fields
    resp = requests.get(url, timeout=40).json()
    status = resp.get('status')
    count = resp.get('meta', {}).get('count')
    data = resp.get('data')
    assert status == 'ok'
    assert len(data) == count
    return(data)

with open('references/tankopedia.json', 'w') as f:
    json.dump(download_tankopedia(), f)
