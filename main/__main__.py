from update_tankopedia import main as update_tankopedia
from update_accounts import main as update_accounts
from update_tanks import main as update_tanks
from calculate_percentiles import main as calculate_percentiles
from calculate_wn8 import main as calculate_wn8
from push_data import main as push_data


def main():

    update_tankopedia()

    update_accounts()

    update_tanks()

    calculate_percentiles()

    calculate_wn8()

    push_data()


if __name__ == '__main__':
    main()
