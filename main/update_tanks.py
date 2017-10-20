import time
import random

import m_wgapi as wgapi
import m_database as db
from m_config import app_id


def main():

    print('Downloading player account data...')


    tankopedia = db.get_tankopedia()
    accounts = db.get_all_accounts()
    max_index = len(accounts) - 1


    #Loop variables.
    end_time = time.time() + 60 * 30
    counter, errors = 0, 0
    fetched_accounts = []


    #Iterating through random accounts.
    while time.time() < end_time:

        #If no more accounts left.
        if not any(accounts):
            print('0 accounts left, stopping...')
            break

        #Getting random account.
        random_index = random.randint(0, max_index)
        account = accounts.pop(random_index)
        max_index -= 1        

        #Requesting player_data.
        try:
            account_id, server = account['account_id'], account['platform']
            status, message, player_data = wgapi.get_player_data(account_id, server, app_id)
            assert status == 'ok', message

        except Exception as e:
            print('Error:', e)
            errors += 1
            if errors > 50:
                print('Too many errors. Terminating...')
                break

        else:
            #Inserting into the database.
            db.insert_player(player_data, tankopedia)
            fetched_accounts.append(account)
            counter += 1

            #Feedback.
            if counter % 100 == 0:
                print(f'Fetched {counter} accounts.')

                #Remove accounts.
                db.remove_accounts(fetched_accounts)
                fetched_accounts = []


    #Loop exit.
    db.remove_accounts(fetched_accounts)
    print(f'Finished. Fetched {counter} accounts with {errors} errors.')
    print('Accounts left:', db.count_accounts())


if __name__ == '__main__':
    main()