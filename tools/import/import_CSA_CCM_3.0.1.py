import os
import csv

FILENAME = "CSA_CCM_3.0.1.csv"

with open(FILENAME) as f:
    reader = csv.reader(f)
    for line in reader:
        domain, process = line[0].split('\n')
        code, number = line[1].split('-')
        activity = line[2].strip()
        print(f"{domain}\t{process}\t{code}\t{number}\t{activity}")
