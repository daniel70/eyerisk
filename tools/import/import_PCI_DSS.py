"""
Import of PCI_DSS
The method to generate the CSV file that can be used by this script is a bit complicated.
- download and install Tabula from http://tabula.technology/
- from the command line, goto tabula folder and start with: java -Dfile.encoding=utf-8 -Xms256M -Xmx1024M -jar tabula.jar
- this starts a local webserver on port 8080
- import CSV file in the application
- select autodetect tables
- manually check and edit all selections
- export to csv

We go through the file. Each time we have a new requirement we save all the procedures together with the requirement.
"""

import os
import csv
import re
#import psycopg2
from datetime import datetime as dt

start = re.compile('\d+\.\d+')
#url = os.environ['DATABASE_URL']
document_id = 2  # Cobit 5.0 value in Control table
##sql = "INSERT INTO risk_control (document_id, ordering, area, domain, process_id, process, practice_id," \
##      "practice_name, activity, created, updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

requirement = ""
procedures = []
guidance = ""

filename = "tabula-PCI_DSS_v3-1.csv"
with open(filename, encoding="utf-8", mode="r") as csv_file: #, psycopg2.connect(url) as conn:
    #c = conn.cursor()
    reader = csv.reader(csv_file)
    next(reader) #skip header
    for line in reader:
##        if reader.line_num == 100:
##            break

        if len(line) != 3:
            for i, j in enumerate(line):
                print(i, j)
            raise IndexError('Incorrect number of columns in line %s' % (reader.line_num))
        
        if line[0].strip() == "PCI DSS Requirements": # repeated table header
            continue

        if start.match(line[0]) and start.match(line[1]): # a new requirement is starting
            NEW_REQUIREMENT = True
            # save the requirement together with all the procedures
            if procedures:
                print("Guidance: ", guidance)
                print("Requirement: ", requirement)
                for procedure in procedures:
                    print("Procedure: ", procedure)
                procedures = []
                print()
                
            requirement = line[0].strip()
            guidance = line[2].strip()
        else:
            NEW_REQUIREMENT = False
            requirement += " " + line[0].strip()
            guidance += " " + line[2].strip()

        if start.match(line[1]): # a new testing procedure is starting
            NEW_PROCEDURE = True
            procedures.append(line[1])
        else:
            NEW_PROCEDURE = False
            procedures[-1] += " " + line[1]
            
            
##        c.execute(sql, (document_id, reader.line_num, line[0].strip(), line[1].strip(), line[2].strip(),
##                        line[3].strip(), line[4].strip(), line[5].strip(), line[6].strip(), dt.now(), dt.now()))
##
##    conn.commit()
