from bs4 import BeautifulSoup
from collections import namedtuple, OrderedDict
from pprint import pprint
from datetime import datetime as dt
import psycopg2
import os

# versions are stored in de "risk_standard" table
current_version = 4
previous_version = 3

url = os.environ['DATABASE_URL']

standard = {
    'ISO/IEC 27002:2013 en': current_version,
    'NEN-ISO/IEC 27002': previous_version,
    'ISO/IEC 27002:2013 nl': current_version,
}

def find_position(values, search):
    """search for a string position in a list, return None if not exists"""
    try:
        pos = values.index(search)
    except ValueError:
        pos = None
    return pos

def get_position_dict(values, search_list):
    """create an ordereddict with all existing items in search_list and their positions"""
    parts = OrderedDict()
    previous = None
    for search in search_list:
        pos = find_position(values, search)
        if pos is not None:
            parts[search] = [pos+1,]
            if previous is not None:
                parts[previous].append(pos)
            previous = search

    if previous is not None:
        parts[previous].append(len(values))
    return parts
    
ident = namedtuple('ident', ['id', 'lang'])
domain = namedtuple('domain', ['id', 'text'])
process = namedtuple('process', ['id', 'name', 'purpose'])
practice = namedtuple('practice', ['id', 'name', 'source', 'control', 'implementation', 'information'])

domains = {}
processes = {}
practices = OrderedDict()
fields = []
strings = {
    "en": ['Control', 'Implementation guidance', 'Other information', 'Source:'],
    "nl": ['Beheersmaatregel', 'Implementatierichtlijn', 'Overige informatie', 'Bron:']
}

def extract(soup, lang):
    sections = soup.find_all(class_='section')
    for section in sections:
        if section.h3:
            id = section.h3.string.split(' ', 1)[0]
            text = section.h3.string
            domains[ident(id, lang)] = domain(id, text)

        if section.h4:
            id, text = section.h4.string.split(' ', 1)
            purpose = section.find('span', class_='sentence').string.split(' ', 1)[1]
            processes[ident(id, lang)] = process(id, text, purpose)

        if section.h5:
            id, name = section.h5.string.split(' ', 1)
            boxes = section.find_all(class_='interpretation-box')
            for box in boxes:
                contr = []
                implementation = []
                information = []
                source = []
                all_strings = list(box.stripped_strings)
                parts = get_position_dict(all_strings, strings[lang])

                positions = parts.get(strings[lang][0])
                if positions:
                    contr = ' '.join(all_strings[positions[0]:positions[1]])
                
                positions = parts.get(strings[lang][1])
                if positions:
                    implementation = ' '.join(all_strings[positions[0]:positions[1]])

                positions = parts.get(strings[lang][2])
                if positions:
                    information = ' '.join(all_strings[positions[0]:positions[1]])

                positions = parts.get(strings[lang][3])
                if positions:
                    source = ' '.join(all_strings[positions[0]:positions[1]])

            practices[ident(id, lang)] = (practice(id, name, source, contr, implementation, information))


extract(BeautifulSoup(open("iso_27001_en.html"), "html.parser"), "en")
extract(BeautifulSoup(open("iso_27001_nl.html"), "html.parser"), "nl")

sql = """INSERT INTO public.risk_control (standard_id, ordering, area, domain, domain_en, domain_nl,
    process_id, process_name, process_name_en, process_name_nl, process_description, process_description_en, process_description_nl, process_purpose, process_purpose_en, process_purpose_nl,
    practice_id, practice_name, practice_name_en, practice_name_nl, practice_governance, practice_governance_en, practice_governance_nl,
    activity_id, activity, activity_en, activity_nl, activity_help, activity_help_en, activity_help_nl,
    created, updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

ordering = 0
with psycopg2.connect(url) as conn:
    c = conn.cursor()
    # delete current entries
    c.execute("DELETE FROM public.risk_control WHERE standard_id = %s", (current_version,))
    conn.commit()
    c.execute("DELETE FROM public.risk_control WHERE standard_id = %s", (previous_version,))
    conn.commit()
    for k, en_practice in practices.items():
        if k.lang == "nl":
            continue
        ordering += 1
        nl_practice = practices[ident(k.id, "nl")]
        process_id = k.id.rsplit('.', 1)[0]
        en_process = processes[ident(process_id, "en")]
        nl_process = processes[ident(process_id, "nl")]
        domain_id = process_id.rsplit('.', 1)[0]
        en_domain = domains[ident(domain_id, "en")]
        nl_domain = domains[ident(domain_id, "nl")]

        fields = [
            standard[en_practice.source],
            ordering,
            'M',
            en_domain.text,
            en_domain.text,
            nl_domain.text,
            en_process.id,
            en_process.name,
            en_process.name,
            nl_process.name,
            '', #process_description is niet aanwezig
            '',
            '',
            en_process.purpose,
            en_process.purpose,
            nl_process.purpose,
            en_practice.id,
            en_practice.name,
            en_practice.name,
            nl_practice.name,
            en_practice.control, # governance
            en_practice.control,
            nl_practice.control,
            1, # activity_id
            en_practice.implementation, # activity
            en_practice.implementation,
            nl_practice.implementation,
            en_practice.information, # activity_help
            en_practice.information,
            nl_practice.information,
            dt.now(),
            dt.now(),
        ]
        c.execute(sql, fields)
               

