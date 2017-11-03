import time


import modules.wgapi as wgapi
import modules.database as db
from secret import app_id


# Reload player account ids and corresponding server names from WG 7 days rating.


def refresh_accounts():

    accounts = wgapi.download_accounts(app_id)
    db.remove_all_accounts()
    db.insert_accounts(accounts)
    print(f'Accounts refreshed. Total: {len(accounts)}')


def main():

    #Getting accounts counter.
    accounts_num = db.count_accounts()
    print(f'Found {accounts_num} accounts in the database.')

    #Conditions for refresh.
    not_enough = accounts_num < 10_000
    sunday = time.gmtime().tm_wday == 6

    if not_enough or sunday:
        if not_enough:
            print('Low count. Refreshing accounts...')
        if sunday:
            print('Its Sunday. Refreshing accounts...')
        refresh_accounts()


if __name__ == '__main__':
    main()
