import sqlite3


from .conn import conn, cur


#Functions for accounts table.


def count():
    return cur.execute('SELECT COUNT(*) FROM accounts;').fetchone()[0]


def get_all():
    #Returns all accounts.

    cur.execute('SELECT * FROM accounts;')
    return [{'account_id': row[0], 'platform': row[1]} for row in cur]


def remove_all():
    cur.execute('DELETE FROM accounts;')
    conn.commit()


def remove(accounts):
    #Input: [{'account_id': 1223456, 'platform': 'ps4'}, ...]

    tuples = [(row['account_id'], row['platform']) for row in accounts]
    cur.executemany('DELETE FROM accounts WHERE account_id = ? AND server = ?;', tuples)
    conn.commit()


def put(accounts):
    #Input: [{'account_id': 1223456, 'platform': 'ps4'}, ...]

    tuples = [(row['account_id'], row['platform']) for row in accounts]
    cur.executemany('INSERT INTO accounts (account_id, server) VALUES (?, ?);', tuples)
    conn.commit()
