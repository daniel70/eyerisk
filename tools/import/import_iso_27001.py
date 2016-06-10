from bs4 import BeautifulSoup
from collections import namedtuple, OrderedDict
from pprint import pprint

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
    

chapter = namedtuple('chapter', ['id', 'text'])
paragraph = namedtuple('paragraph', ['id', 'text', 'objective'])
control = namedtuple('control', ['id', 'text', 'source', 'control', 'implementation', 'information'])

chapters = []
paragraphs = []
controls = []


soup = BeautifulSoup(open("iso_27001_en.html"), "html.parser")
sections = soup.find_all(class_='section')
for section in sections:
    if section.h3:
        id, text = section.h3.string.split(' ', 1)
        chapters.append(chapter(id, text))

    if section.h4:
        id, text = section.h4.string.split(' ', 1)
        objective = section.find('span', class_='sentence').string.split(' ', 1)[1]
        paragraphs.append(paragraph(id, text, objective))

    if section.h5:
        id, text = section.h5.string.split(' ', 1)
        boxes = section.find_all(class_='interpretation-box')
        for box in boxes:
            contr = []
            implementation = []
            information = []
            source = []
            all_strings = list(box.stripped_strings)
            parts = get_position_dict(all_strings, ['Control', 'Implementation guidance', 'Other information', 'Source:'])

            positions = parts.get('Control')
            if positions:
                contr = all_strings[positions[0]:positions[1]]
            
            positions = parts.get('Implementation guidance')
            if positions:
                implementation = all_strings[positions[0]:positions[1]]

            positions = parts.get('Other information')
            if positions:
                information = all_strings[positions[0]:positions[1]]

            positions = parts.get('Source:')
            if positions:
                source = all_strings[positions[0]:positions[1]]

        controls.append(control(id, text, source, contr, implementation, information))
