"""
Import `filename` into the database table Question.
"""
import os
import csv
import psycopg2
from datetime import datetime as dt
from collections import namedtuple

nu = dt.now()
process = namedtuple('proces', ['area', 'domain', 'process_id', 'process_name', 'process_description', 'process_purpose'])
practice = namedtuple('practice', ['practice_id', 'practice_name', 'practice_governance'])
activity = namedtuple('activity', ['practice_id', 'activity'])
processes = {}
practices = {}

url = os.environ['DATABASE_URL']
standard_id = 2  # Cobit 5.0 value in Standard table
##sql = """INSERT INTO public.risk_control (standard_id, ordering, area, domain, domain_en,
##    process_id, process_name, process_name_en, process_description, process_description_en, process_purpose, process_purpose_en,
##    practice_id, practice_name, practice_name_en, practice_governance, practice_governance_en,
##    activity_id, activity, activity_en, activity_help, activity_help_en,
##    created, updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""


sql_domain = """INSERT INTO public.risk_controldomain (standard_id, ordering, area, domain, domain_en) VALUES (%s,%s,%s,%s,%s) returning id"""
sql_process = """INSERT INTO public.risk_controlprocess (controldomain_id, ordering, process_id, process_name, process_name_en, process_description, process_description_en, process_purpose, process_purpose_en) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id"""
sql_practice = """INSERT INTO public.risk_controlpractice (controlprocess_id, ordering, practice_id, practice_name, practice_name_en, practice_governance, practice_governance_en) VALUES (%s,%s,%s,%s,%s,%s,%s) returning id"""
sql_activity = """INSERT INTO public.risk_controlactivity (controlpractice_id, ordering, activity_id, activity, activity_en, activity_help, activity_help_en, created, updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id"""

domain_ids = {}
process_ids = {}
practice_ids = {}

with open("cobit_5.0_all_en_processes.csv", encoding="utf-8", mode="r") as f_processes, \
         open("cobit_5.0_all_en_practices.csv", encoding="utf-8", mode="r") as f_practices, \
             open("cobit_5.0_all_en_activities.csv", encoding="utf-8", mode="r") as f_activities, \
                 psycopg2.connect(url) as conn:
    c = conn.cursor()
    c.execute("DELETE FROM public.risk_controldomain WHERE standard_id = %s", (standard_id,))
    conn.commit()
    reader = csv.reader(f_processes)
    next(reader) #skip header
    for line in reader:
        p = process(*line)
        if not p.domain in domain_ids:
            c.execute(sql_domain, (standard_id, len(domain_ids)+1, p.area[0], p.domain, p.domain))
            id = c.fetchone()[0]
            conn.commit()
            domain_ids[p.domain] = id

        if not p.process_id in process_ids:
            c.execute(sql_process, (domain_ids[p.domain], len(process_ids)+1, p.process_id, p.process_name, p.process_name, p.process_description, p.process_description, p.process_purpose, p.process_purpose))
            id = c.fetchone()[0]
            conn.commit()
            process_ids[p.process_id] = id
        
##        processes[p.process_id] = p

    reader = csv.reader(f_practices)
    next(reader) #skip header
    for line in reader:
        p = practice(*line)
        if not p.practice_id in practice_ids:
            process_id = p.practice_id.split('.', 1)[0]
            c.execute(sql_practice, (process_ids[process_id], len(practice_ids)+1, p.practice_id, p.practice_name, p.practice_name, p.practice_governance, p.practice_governance))
            id = c.fetchone()[0]
            conn.commit()
            practice_ids[p.practice_id] = id
        
##        practices[p.practice_id] = p

    reader = csv.reader(f_activities)
    next(reader) #skip header
    for line in reader:
        a = activity(*line)
        activity_id = a.activity.split('.', 1)[0]
        c.execute(sql_activity, (practice_ids[a.practice_id], reader.line_num, activity_id, a.activity, a.activity, '', '', nu, nu))
        conn.commit

