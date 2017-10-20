import sqlite3


conn = sqlite3.connect('sqlite.db')
cur = conn.cursor()


cur.execute('''
    CREATE TABLE IF NOT EXISTS tanks (
        tank_id INTEGER,
        last_battle_time INTEGER,
        account_id INTEGER,
        server TEXT,
        battle_life_time INTEGER,
        battles INTEGER,
        capture_points INTEGER,
        damage_assisted_radio INTEGER,
        damage_assisted_track INTEGER,
        damage_dealt INTEGER,
        damage_received INTEGER,
        direct_hits_received INTEGER,
        dropped_capture_points INTEGER,
        explosion_hits INTEGER,
        explosion_hits_received INTEGER,
        frags INTEGER,
        hits INTEGER,
        losses INTEGER,
        mark_of_mastery INTEGER,
        max_frags INTEGER,
        max_xp INTEGER,
        no_damage_direct_hits_received INTEGER,
        piercings INTEGER,
        piercings_received INTEGER,
        shots INTEGER,
        spotted INTEGER,
        survived_battles INTEGER,
        trees_cut INTEGER,
        wins INTEGER,
        xp INTEGER,
        PRIMARY KEY (tank_id, last_battle_time, account_id, server)
);''')


cur.execute('''
    CREATE TABLE IF NOT EXISTS tankopedia (
        tank_id INTEGER PRIMARY KEY,
        updated_at INTEGER,
        name TEXT,
        short_name TEXT,
        nation TEXT,
        is_premium INTEGER,
        tier INTEGER,
        type TEXT
);''')


cur.execute('''
    CREATE TABLE IF NOT EXISTS percentiles (
        tank_id INTEGER PRIMARY KEY,
        updated_at INTEGER,
        data BLOB
);''')


cur.execute('''
    CREATE TABLE IF NOT EXISTS percentiles_generic (
        tier INTEGER,
        type TEXT,
        updated_at INTEGER,
        data BLOB,
        PRIMARY KEY (tier, type)
);''')


cur.execute('''
    CREATE TABLE IF NOT EXISTS wn8 (
        tank_id INTEGER PRIMARY KEY,
        expFrag REAL,
        expDamage REAL,
        expSpot REAL,
        expDef REAL,
        expWinRate REAL
);''')


cur.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER,
        server TEXT
);''')


conn.commit()
conn.close()
