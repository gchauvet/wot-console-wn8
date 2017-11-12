import sqlite3
import pickle
import time


from .conn import conn, cur


#History table.


def put(list_of_dicts):

    columns = [
        'tank_id', 'created_at', 'recency',
        'battle_life_time', 'capture_points', 'damage_assisted_radio',
        'damage_dealt', 'damage_received', 'direct_hits_received',
        'frags', 'hits', 'losses', 'piercings', 'piercings_received',
        'shots', 'spotted', 'survived_battles', 'wins', 'xp'
    ]

    columns_str = ', '.join(columns)
    question_marks = ', '.join(['?' for i in columns])

    rows = []
    for item in list_of_dicts:
        rows.append([item[col] for col in columns])

    cur.executemany(f'INSERT INTO history ({columns_str}) VALUES ({question_marks})', rows)
    conn.commit()
