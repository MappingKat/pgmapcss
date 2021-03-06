from .parse_defines import parse_defines
from .parse_selectors import parse_selectors
from .parse_properties import parse_properties
from .strip_comments import strip_comments
from .ParseFile import *
import pgmapcss.mapnik
import copy

def parse_file(stat, filename=None, base_style=None, content=None):
    if not 'max_prop_id' in stat:
        stat['max_prop_id'] = 0

    if base_style:
        parse_file(stat, content=pgmapcss.mapnik.get_base_style(base_style))

    if not 'statements' in stat:
        stat['statements'] = []
        stat['defines'] = {}

    f = ParseFile(filename=filename, content=content)

    f.set_content(strip_comments(f))

# read statements until there's only whitespace left
    while True:
        while True:
            r = parse_defines(stat, f)
            if not r:
                break;
            elif r and r[0] == 'import':
                parse_file(stat, r[1])

        if f.match('\s*$'):
            return True

        selectors = []
        parse_selectors(selectors, f)

        properties = []
        parse_properties(properties, f)

        for i in selectors:
            statement = i.copy()
            statement['properties'] = copy.deepcopy(properties)
            stat['statements'].append(statement)
            statement['id'] = stat['max_prop_id']
            stat['max_prop_id'] = stat['max_prop_id'] + 1

            for prop in statement['properties']:
                prop['statement'] = statement
                prop['id'] = stat['max_prop_id']
                stat['max_prop_id'] = stat['max_prop_id'] + 1
