import sqlite3


#Global connection variables.


conn = sqlite3.connect('sqlite.db')
cur = conn.cursor()
