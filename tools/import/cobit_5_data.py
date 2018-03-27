import psycopg2
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
 
DATABASE_URL = os.environ['DATABASE_URL']

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_google_drive.json', scope)
client = gspread.authorize(creds)
 
# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("cobit 5 data").sheet1
 
# Extract and print all of the values
raci = sheet.get_all_records()

col_stmnt = "{} = models.CharField(_('{}'), max_length=1, blank=True, choices=RACI_CHOICES)"
sel_stmnt = "SELECT id FROM risk_controlpractice WHERE practice_id = %s"
del_stmnt = "DELETE FROM risk_controlpracticeraci WHERE controlpractice_id = %s"
ins_stmnt = "INSERT INTO risk_controlpracticeraci (controlpractice_id, {}) VALUES ({}, {})"

if not raci:
    print("No rows in spreadsheet were found")
    quit()
    
with psycopg2.connect(DATABASE_URL) as conn:
    cur = conn.cursor()
    for row in raci:
        # select practice id then delete this raci
        raci_id = row.pop('PracticeID') # e.g. EDM01.01
        cur.execute(sel_stmnt, (raci_id, ))
        record = cur.fetchone()
        if not record:
            print('Row with practice_id {} does not exist in spreadsheet'.format(raci_id))
            quit()

        control_practice_id = record[0] # e.g. 229
        print('Deleting record {} (id: {})'.format(raci_id, control_practice_id))
        cur.execute(del_stmnt, (control_practice_id,))

        cols = ', '.join([key.lower().replace(' ', '_') for key in row.keys()])
        vals = ', '.join([repr(v) for v in row.values()])
        cur.execute(ins_stmnt.format(cols, control_practice_id, vals))

