"""
Import `filename` into the database table Question.
"""
import os
import csv
import psycopg2
from datetime import datetime as dt

url = os.environ['DATABASE_URL']
document_id = 2  # Cobit 5.0 value in Document table
sql = "INSERT INTO compliance_question (document_id, ordering, code, code_text, text, description, created, updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"

filename = "cobit_5_2016.csv"
with open(filename, encoding="utf-8", mode="r") as csv_file, psycopg2.connect(url) as conn:
    c = conn.cursor()
    reader = csv.reader(csv_file)
    next(reader) #skip header
    for line in reader:
        if not line[2]:
            # sometimes there is no question, we will skip for now
            continue
        
        code, code_text = line[0].split(" ", 1)
        description = line[1]
        extra, text = line[2].split(" ", 1)
        code = '.'.join([code, '0'+extra.rstrip('. ')])
        
        c.execute(sql, (document_id, reader.line_num, code.strip(), code_text.strip(), text.strip(), description.strip(), dt.now(), dt.now()))

    conn.commit()
