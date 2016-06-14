"""
Import `filename` into the database table Question.
"""
import os
import csv
import psycopg2
from datetime import datetime as dt
from collections import namedtuple

process = namedtuple('proces', ['area', 'domain', 'process_id', 'process_name', 'process_description', 'process_purpose'])
practice = namedtuple('practice', ['practice_id', 'practice_name', 'practice_governance'])
activity = namedtuple('activity', ['practice_id', 'activity'])
processes = {}
practices = {}

url = os.environ['DATABASE_URL']
standard_id = 2  # Cobit 5.0 value in Standard table
sql = """INSERT INTO public.risk_control (standard_id, ordering, area, domain, domain_en,
    process_id, process_name, process_name_en, process_description, process_description_en, process_purpose, process_purpose_en,
    practice_id, practice_name, practice_name_en, practice_governance, practice_governance_en,
    activity_id, activity, activity_en, activity_help, activity_help_en,
    created, updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

with open("cobit_5.0_all_en_processes.csv", encoding="utf-8", mode="r") as f_processes, \
         open("cobit_5.0_all_en_practices.csv", encoding="utf-8", mode="r") as f_practices, \
             open("cobit_5.0_all_en_activities.csv", encoding="utf-8", mode="r") as f_activities, \
                 psycopg2.connect(url) as conn:
    c = conn.cursor()
    c.execute("DELETE FROM public.risk_control WHERE standard_id = %s", (standard_id,))
    conn.commit()
    reader = csv.reader(f_processes)
    next(reader) #skip header
    for line in reader:
        p = process(*line)
        processes[p.process_id] = p

    reader = csv.reader(f_practices)
    next(reader) #skip header
    for line in reader:
        p = practice(*line)
        practices[p.practice_id] = p

    reader = csv.reader(f_activities)
    next(reader) #skip header
    for line in reader:
        a = activity(*line)
        process_id = a.practice_id.split('.', 1)[0]
        activity_id = a.activity.split('.', 1)[0]
        proc = processes[process_id]
        prac = practices[a.practice_id]
        #print(reader.line_num, activity_id)
        c.execute(sql, (
            standard_id,
            reader.line_num,
            proc.area[0],
            proc.domain,
            proc.domain,
            proc.process_id,
            proc.process_name,
            proc.process_name,
            proc.process_description,
            proc.process_description,
            proc.process_purpose,
            proc.process_purpose,
            prac.practice_id,
            prac.practice_name,
            prac.practice_name,
            prac.practice_governance,
            prac.practice_governance,
            activity_id,
            a.activity,
            a.activity,
            '',
            '',
            dt.now(),
            dt.now()
            )
        )
        conn.commit()    

