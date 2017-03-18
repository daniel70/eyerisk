import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
 
DATABASE_URL = os.environ['DATABASE_URL']
print(DATABASE_URL)


# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_google_drive.json', scope)
client = gspread.authorize(creds)
 
# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("cobit 5 data").sheet1
 
# Extract and print all of the values
raci = sheet.get_all_records()
#print(list_of_hashes)
