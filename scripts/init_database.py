import sqlite3


conn = sqlite3.connect('sqlite.db')
cur = conn.cursor()


#Main tanks storage.
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


#Tankopedia.
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


#Percentiles.
#data = python pickle object.
cur.execute('''
    CREATE TABLE IF NOT EXISTS percentiles (
        tank_id INTEGER PRIMARY KEY,
        updated_at INTEGER,
        data BLOB
);''')


#Generic percentiles.
#data = python pickle object.
cur.execute('''
    CREATE TABLE IF NOT EXISTS percentiles_generic (
        tier INTEGER,
        type TEXT,
        updated_at INTEGER,
        data BLOB,
        PRIMARY KEY (tier, type)
);''')


#WN8 expected values.
cur.execute('''
    CREATE TABLE IF NOT EXISTS wn8 (
        tank_id INTEGER PRIMARY KEY,
        expFrag REAL,
        expDamage REAL,
        expSpot REAL,
        expDef REAL,
        expWinRate REAL
);''')


#Temporary account info storage.
cur.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER,
        server TEXT
);''')


#Historical medians of the ratios: metric / battles.
#recency: median of (int(time.time()) - last_battle_time)
cur.execute('''
    CREATE TABLE IF NOT EXISTS history (
        tank_id INTEGER,
        created_at INTEGER,
        recency INTEGER,
        battle_life_time REAL,
        capture_points REAL,
        damage_assisted_radio REAL,
        damage_dealt REAL,
        damage_received REAL,
        direct_hits_received REAL,
        frags REAL,
        hits REAL,
        losses REAL,
        piercings REAL,
        piercings_received REAL,
        shots REAL,
        spotted REAL,
        survived_battles REAL,
        wins REAL,
        xp REAL,
        PRIMARY KEY (tank_id, created_at)
);''')


conn.commit()
conn.close()
