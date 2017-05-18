# adventures in psycopg
import os, sys
import psycopg2

print('version: {}'.format(psycopg2.__version__))

try:
    DATABASE_URL = os.environ['DATABASE_URL']
except KeyError:
    print('DATABASE_URL environment variable does not exist.')
    quit()
    
with psycopg2.connect(DATABASE_URL) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM risk_controlpracticeraci")

    for desc in cur.description:
        print(desc)
        
    
    
    rows = conn.fetchall()
    print(rows[:10])

