import psycopg2, psycopg2.extras
import re
import unicodedata
import os
import sys

#risk_controlactivity, 1215
url = os.environ['DATABASE_URL']
upd_sql = "UPDATE risk_controlactivity SET activity = %s, updated = current_timestamp WHERE id = %s"
upd_en_sql = "UPDATE risk_controlactivity SET activity_en = %s, updated = current_timestamp WHERE id = %s"
upd_nl_sql = "UPDATE risk_controlactivity SET activity_nl = %s, updated = current_timestamp WHERE id = %s"
upd_help_sql = "UPDATE risk_controlactivity SET activity_help = %s, updated = current_timestamp WHERE id = %s"
upd_help_en_sql = "UPDATE risk_controlactivity SET activity_help_en = %s, updated = current_timestamp WHERE id = %s"
upd_help_nl_sql = "UPDATE risk_controlactivity SET activity_help_nl = %s, updated = current_timestamp WHERE id = %s"

with psycopg2.connect(url) as conn:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""SELECT id, activity, activity_en, activity_nl, activity_help, activity_help_en, activity_help_nl FROM risk_controlactivity ORDER BY id""")
    rows = cur.fetchall()
    for row in rows:
        act_org = row['activity']
        if act_org == "{}":
            print("emptying record", row['id'])
            cur.execute(upd_sql, ['', row['id']])
            continue
        
        act_new = re.sub(r' (\w{1})\)\s+', ' \n\\1) ', unicodedata.normalize("NFKD", act_org))
        if act_new != act_org:
            print("updating record", row['id'])
            cur.execute(upd_sql, [act_new, row['id']])

        #activity_en
        act_en_org = row['activity_en']
        if act_en_org == "{}":
            print("emptying record", row['id'])
            cur.execute(upd_en_sql, ['', row['id']])
            continue
        
        act_en_new = re.sub(r' (\w{1})\)\s+', ' \n\\1) ', unicodedata.normalize("NFKD", act_en_org))
        if act_en_new != act_en_org:
            print("updating record", row['id'])
            cur.execute(upd_en_sql, [act_en_new, row['id']])

        #activity_nl
        act_nl_org = row['activity_nl']
        if act_nl_org is None:
            continue
        
        if act_nl_org == "{}":
            print("emptying record", row['id'])
            cur.execute(upd_nl_sql, ['', row['id']])
            continue

        act_nl_new = re.sub(r' (\w{1})\)\s+', ' \n\\1) ', unicodedata.normalize("NFKD", act_nl_org))
        if act_nl_new != act_nl_org:
            print("updating record", row['id'])
            cur.execute(upd_nl_sql, [act_nl_new, row['id']])

        #activity_help
        act_help_org = row['activity_help']
        if act_help_org == "{}":
            print("emptying record", row['id'])
            cur.execute(upd_help_sql, ['', row['id']])
            continue
        
        act_help_new = re.sub(r' (\w{1})\)\s+', ' \n\\1) ', unicodedata.normalize("NFKD", act_help_org))
        if act_help_new != act_help_org:
            print("updating record", row['id'])
            cur.execute(upd_help_sql, [act_help_new, row['id']])

        #activity_help_en
        act_help_en_org = row['activity_help_en']
        if act_help_en_org == "{}":
            print("emptying record", row['id'])
            cur.execute(upd_help_en_sql, ['', row['id']])
            continue
        
        act_help_en_new = re.sub(r' (\w{1})\)\s+', ' \n\\1) ', unicodedata.normalize("NFKD", act_help_en_org))
        if act_help_en_new != act_help_en_org:
            print("updating record", row['id'])
            cur.execute(upd_help_en_sql, [act_help_en_new, row['id']])

        #activity_help_nl
        act_help_nl_org = row['activity_help_nl']
        if act_help_nl_org is None:
            continue
        
        if act_help_nl_org == "{}":
            print("emptying record", row['id'])
            cur.execute(upd_help_nl_sql, ['', row['id']])
            continue

        act_help_nl_new = re.sub(r' (\w{1})\)\s+', ' \n\\1) ', unicodedata.normalize("NFKD", act_help_nl_org))
        if act_help_nl_new != act_help_nl_org:
            print("updating record", row['id'])
            cur.execute(upd_help_nl_sql, [act_help_nl_new, row['id']])

    conn.commit()


