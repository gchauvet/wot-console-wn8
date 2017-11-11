import sys
import time
import json
import requests


from .database import export as db
from .secret import hosts


#Main routine to push data to remote hosts.

#Send json-encoded payload in post body of the request.
#Authorization via 'access_key' in the body.
#HTTPS must be used for security.


def post_data(url, payload):
    # import gzip
    # import pickle
    start = time.time()

    attempts, max_attempts = 0, 2
    while attempts < max_attempts:
        try:
            resp = requests.post(url, timeout=15, json=payload).json()
            status, message = resp['status'], resp['message']
            assert status == 'ok', message

        except requests.exceptions.Timeout:
            print('ERROR: request timeout')
            attempts += 1

        except (requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
            print('ERROR: connection error, check supplied URL')
            attempts += 1

        except json.decoder.JSONDecodeError:
            print('ERROR: Cant decode json')
            attempts += 1

        except AssertionError as e:
            print('ERROR:', e)
            attempts += 1

        except KeyError:
            print('ERROR: json response doesnt contain \'status\' or \'message\' keys')
            attempts += 1

        else:
            #Feedback.
            took = round(time.time() - start, 2)
            kib = round(sys.getsizeof(json.dumps(payload)) / 1024, 2)
            print(f'SUCCESS: Took: {took} s. Size: {kib} KiB')
            # took = round(time.time() - start, 2)
            # kib = round(sys.getsizeof(gzip.compress(json.dumps(payload).encode())) / 1024, 2)
            # print(f'Done. Took: {took} s. Size: {kib} KiB')
            # took = round(time.time() - start, 2)
            # kib = round(sys.getsizeof(pickle.dumps(payload)) / 1024, 2)
            # print(f'Done. Took: {took} s. Size: {kib} KiB')
            return


def main():

    for host in hosts:

        url, access_key = host['url'], host['access_key']
        print(f'INFO: Sending data to {url}')


        #Tankopedia.
        print('INFO: Pushing tankopedia...')
        data = db.export_tankopedia()
        payload = {
            'name':       'tankopedia',
            'data':       data,
            'count':      len(data),
            'access_key': access_key
        }
        post_data(url, payload)


        #Continue only on sunday.
        if time.gmtime().tm_wday != 6:
            return


        #Percentiles.
        print('INFO: Pushing percentiles...')
        data = db.export_percentiles()
        payload = {
            'name':       'percentiles',
            'data':       data,
            'count':      len(data),
            'access_key': access_key
        }
        post_data(url, payload)


        #Percentiles generic.
        print('INFO: Pushing percentiles generic...')
        data = db.export_percentiles_generic()
        payload = {
            'name':       'percentiles_generic',
            'data':       data,
            'count':      len(data),
            'access_key': access_key
        }
        post_data(url, payload)


        #WN8.
        print('INFO: Pushing WN8...')
        data = db.export_wn8_exp_values()
        payload = {
            'name':       'wn8',
            'data':       data,
            'count':      len(data),
            'access_key': access_key
        }
        post_data(url, payload)


if __name__ == '__main__':
    main()
