import json


DEFAULT_CONFIG_PATH = 'dataminer_config.json'
DEFAULT_CONFIG = {
    #app_id to contact WG API services.
    'app_id': 'demo',
    #List of hosts to push data to.
    'hosts': [
        {'url': 'http://127.0.0.1:5000/update/', 'access_key': '12345'}
    ]
}


def create():
    with open(DEFAULT_CONFIG_PATH, 'w') as f:
        json.dump(DEFAULT_CONFIG, f)


def read():
    try:
        with open(DEFAULT_CONFIG_PATH, 'r') as f:
            config = json.load(f)
        config['app_id'], config['hosts']

    except FileNotFoundError:
        print('WARNING: Config file doesnt exist.')
        print('Creating config with default credentials in project folder...')
        create()
        config = DEFAULT_CONFIG

    except (KeyError, json.JSONDecodeError):
        print('WARNING: config file cant be read. Using default credentials.')
        config = DEFAULT_CONFIG

    return config['app_id'], config['hosts']


app_id, hosts = read()
