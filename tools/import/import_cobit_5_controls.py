"""
Import `filename` into the database table Question.
"""
import os
import csv
import psycopg2
from datetime import datetime as dt

url = os.environ['DATABASE_URL']
document_id = 2  # Cobit 5.0 value in Control table
sql = "INSERT INTO risk_control (document_id, ordering, area, domain, process_id, process, practice_id," \
      "practice_name, activity, created, updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

filename = "12.COBIT5-Governance-and-Management-Practices-Activities_April2014.csv"
with open(filename, encoding="utf-8", mode="r") as csv_file, psycopg2.connect(url) as conn:
    c = conn.cursor()
    reader = csv.reader(csv_file)
    next(reader) #skip header
    for line in reader:
        c.execute(sql, (document_id, reader.line_num, line[0].strip(), line[1].strip(), line[2].strip(),
                        line[3].strip(), line[4].strip(), line[5].strip(), line[6].strip(), dt.now(), dt.now()))

    conn.commit()
