import time


from . import wgapi
from .database import t_accounts as db


#Main routine to reload player account ids and corresponding server names from WG 7 days rating.


def main():

    #Getting accounts counter.
    accounts_num = db.count()
    print(f'INFO: Found {accounts_num} accounts in the database.')


    #Conditions for refresh.
    not_enough = accounts_num < 10_000
    sunday = time.gmtime().tm_wday == 6


    if not_enough or sunday:

        if not_enough:
            print('INFO: Low count. Refreshing accounts...')
        if sunday:
            print('INFO: Its Sunday. Refreshing accounts...')

        accounts = wgapi.download_accounts()
        db.remove_all()
        db.put(accounts)

        print(f'SUCCESS: Accounts refreshed. Total: {len(accounts)}')


if __name__ == '__main__':
    main()
