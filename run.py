from main import *


def main():

    print('######## Updating tankopedia...')
    update_tankopedia()

    print('######## Updating accounts...')
    update_accounts()

    print('######## Updating tanks...')
    update_tanks()

    print('######## Calculating percentiles...')
    calculate_percentiles()

    print('######## Calculating WN8...')
    calculate_wn8()

    print('######## Calculating history...')
    calculate_history()

    print('######## Pushing the data...')
    push_data()


if __name__ == '__main__':
    main()
