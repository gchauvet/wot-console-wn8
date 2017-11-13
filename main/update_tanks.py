import time
import random


from . import wgapi
from .database.t_tankopedia import get_tankopedia
from .database.t_tanks import insert_player
from .database import t_accounts as db_accounts


# Update tanks data.


def main():

    tankopedia = get_tankopedia()
    accounts = db_accounts.get_all()
    max_index = len(accounts) - 1


    #Loop variables.
    end_time = time.time() + 60 * 60
    max_counter = 5000
    counter, errors = 0, 0
    fetched_accounts = []


    #Iterating through random accounts.
    while time.time() < end_time and counter <= max_counter:

        #If no more accounts left.
        if not any(accounts):
            print('WARNING: 0 accounts left in the database. Terminating...')
            break

        #Getting random account.
        random_index = random.randint(0, max_index)
        account = accounts.pop(random_index)
        max_index -= 1

        #Requesting player_data.
        try:
            account_id, server = account['account_id'], account['platform']
            status, message, player_data = wgapi.get_player_data(account_id, server)
            assert status == 'ok', message

        except Exception as e:
            print('ERROR:', e)
            errors += 1
            if errors > 50:
                print('WARNING: Too many errors. Terminating...')
                break

        else:
            #Inserting into the database.
            insert_player(player_data, tankopedia)
            fetched_accounts.append(account)
            counter += 1

            #Feedback & release downloaded accounts.
            if counter % 500 == 0:
                print(f'INFO: Fetched {counter} accounts.')

                #Remove accounts.
                db_accounts.remove(fetched_accounts)
                fetched_accounts = []


    #Loop exit.
    db_accounts.remove(fetched_accounts)
    print(f'SUCCESS: Fetched {counter} accounts with {errors} errors.')
    print('INFO: Accounts left:', db_accounts.count())


if __name__ == '__main__':
    main()
