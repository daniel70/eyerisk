"""
Import `filename` into the database table Question.
"""
import os
import csv
import psycopg2
from datetime import datetime as dt
url = os.environ['DATABASE_URL']
sql_categorie = """INSERT INTO public.risk_scenariocategory values (%s,%s)"""
sql_scenario = """INSERT INTO public.risk_scenario values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

categorie_ids = []

with open("risk_scenarios.csv") as f, psycopg2.connect(url) as conn:
    c = conn.cursor()
    count = 0
    reader = csv.DictReader(f)
    
    for line in reader:
        # strip spaces and remove line feeds from all values
        line = dict([k, v.replace('\n', ' ').strip()] for k, v in line.items())
        
        if line['Title'].strip() == '':
            continue

        nr, name = line['Category'].split(' ', 1)
        if nr not in categorie_ids:
            c.execute(sql_categorie, (nr, name))
            categorie_ids.append(nr)
            
        count += 1
        c.execute(sql_scenario, (
            line['Reference'],
            line['Title'],
            nr,
            line['Risk_scenario'],
            line['Threat_type'],
            line['Actor'],
            line['Event'],
            line['Asset/Resource(Cause)'],
            line['Asset/Resource(Effect)'],
            line['Time'],
            line['IT_benefit/value_enablement'],
            line['IT_programme_and_project_delivery'],
            line['IT_operations_and_service_delivery'],
            line['RiskAvoidance'],
            line['RiskAcceptance'],
            line['RiskSharing/Transfer'],
            line['RiskMitigation'],
            '',
            ''
            )
        )
