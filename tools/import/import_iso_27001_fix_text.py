import psycopg2, psycopg2.extras
import re
import unicodedata
import os
import sys

##r1 = "1. Analyse and identify the internal and external environmental factors (legal, regulatory and contractual obligations) and trends in the business environment that may influence governance design."
##print(r1.encode())
##print("\n")
##print(re.sub(r' (\w{1})\)\s+', ' \n\\1) ', unicodedata.normalize("NFKD", r1)).encode())
##
##sys.exit()

#risk_controlactivity, 1215
url = os.environ['DATABASE_URL']
upd_sql = """
    UPDATE risk_controlactivity
    SET activity = ?, updated = current_timestamp
    WHERE id = ?
"""

with psycopg2.connect(url) as conn:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""SELECT id, activity, activity_en, activity_nl, activity_help, activity_help_en, activity_help_nl FROM risk_controlactivity ORDER BY id""")
    rows = cur.fetchall()
    for row in rows:
        act_org = row['activity']
        if act_org == "{}":
            print("emptying record", row['id'])
            continue
        
        act_new = re.sub(r' (\w{1})\)\s+', ' \n\\1) ', unicodedata.normalize("NFKD", act_org))
        if act_new != act_org:
            print("updating record", row['id'])

##        
##t = "An organization should ensure that: a)     an adequate management structure is in place to prepare for, mitigate and respond to a disruptive event using personnel with the necessary authority, experience and competence; b)    incident response personnel with the necessary responsibility, authority and competence to manage an incident and maintain information security are nominated; c)     documented plans, response and recovery procedures are developed and approved, detailing how the organization will manage a disruptive event and will maintain its information security to a predetermined level, based on management-approved information security continuity objectives (see 17.1.1 ). According to the information security continuity requirements, the organization should establish, document, implement and maintain: a)     information security controls within business continuity or disaster recovery processes, procedures and supporting systems and tools; b)    processes, procedures and implementation changes to maintain existing information security controls during an adverse situation; c)     compensating controls for information security controls that cannot be maintained during an adverse situation."
##
##print("before\n")
##print(t.encode())
##
##print("\nafter\n")
##u = unicodedata.normalize("NFKD", t)
##r = re.sub(r' (\w+)\)\s+', ' \n\\1) ', u)
##print(r)
