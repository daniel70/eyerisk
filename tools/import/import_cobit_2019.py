import psycopg2
import datetime
import csv
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError('DATABASE_URL is not set.')

now = datetime.datetime.now()
standard = "Cobit 2019"
auto_delete = False
standard_id = None
practice_ids = {}

with psycopg2.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM risk_standard WHERE name = %s", (standard,) )
        recs = cur.fetchall()

        if recs and not auto_delete:
            raise ValueError(f'{standard} already exists. Please remove existing records first.')
        elif recs and auto_delete:
            # delete all records from Cobit 2019
            pass
        
        # insert and return the new standard
        cur.execute("""
            INSERT INTO risk_standard (name, is_active, created, updated)
            VALUES (%s, %s, %s, %s)
            RETURNING id""",
            (standard, True, now, now)
        )
        standard_id = cur.fetchone()[0]
        print(f"standard id: {standard_id}")

        # in practices staan de gegevens voor domain + process + practice
        # Area en Domain --> controldomain
        
        # Objective ID --> process_id
        # Objective --> process_name
        # Objective Description --> process_description
        # Objective Purpose Statement --> process_purpose

        # Practice ID --> practice_id e.g. EDM01.01
        # Practice Name --> practice_name
        # Practice Description --> practice_governance
        
        with open('practices.csv') as csvfile:
            
            current_domain = None
            domain_id = None
            domain_order = 1

            current_process = None
            process_id = None
            process_order = 1
            
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):

                if row['Area']:
                    # insert control domain if necessary
                    if current_domain != row['Domain']:
                        sql = """
                        INSERT INTO risk_controldomain (ordering, area, domain, domain_en, standard_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """
                        cur.execute(sql, (domain_order, row['Area'][0], row['Domain'], row['Domain'], standard_id))        
                        domain_id = cur.fetchone()[0]
                        domain_order += 1
                        current_domain = row['Domain']

                    # insert control process
                    sql = """
                    INSERT INTO risk_controlprocess (ordering, process_id, process_name, process_name_en,
                    process_description, process_description_en, process_purpose, process_purpose_en, controldomain_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """
                    cur.execute(sql, (process_order, row['Objective ID'], row['Objective'], row['Objective'], row['Objective Description'], row['Objective Description'],
                                      row['Objective Purpose Statement'], row['Objective Purpose Statement'], domain_id))
                    process_id = cur.fetchone()[0]
                    process_order += 1

                # insert control practice
                sql = """
                INSERT INTO risk_controlpractice (ordering, practice_id, practice_name, practice_name_en, practice_governance, practice_governance_en, controlprocess_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                cur.execute(sql, (i+1, row['Practice ID'], row['Practice Name'], row['Practice Name'], row['Practice Description'], row['Practice Description'], process_id))

                # save a dict with the id's of practice_ids { 'EDM01.01': 42 }
                practice_ids[row['Practice ID']] = cur.fetchone()[0]

        with open('activities.csv') as csvfile:
            practice_pk = None
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                # find the practice_id in the dictionary and save the record in risk_controlactivity
                practice_pk = practice_ids[row['Practice ID']]
                sql = """
                INSERT INTO risk_controlactivity (ordering, activity_id, activity, activity_en, activity_help, created, updated, controlpractice_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql, (i+1, row['Activity'][0], row['Activity'], row['Activity'], '', now, now, practice_pk))
                
print(standard_id)
