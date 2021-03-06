from .parse_condition import parse_condition
from .ParseError import *
import re

def parse_selector_part(to_parse, object_class_selector='\*|[a-z_]+'):
    max_scale_denominator = 3.93216e+08;
    current = {}
    current['conditions']  = []
    current['pseudo_element'] = 'default'
    current['min_scale'] = 0
    current['max_scale'] = None

# parse object class (way, node, canvas, ...)
    if to_parse.match('\s*(' + object_class_selector + ')'):
        if to_parse.match_group(1) == '*':
            current['type'] = True
        else:
            current['type'] = to_parse.match_group(1)

    else:
        raise ParseError(to_parse, 'Can\'t parse object class')

# parse classes
    while to_parse.match('\.([a-zA-Z0-9_]+)'):
        if 'classes' in current:
            pass
        else:
            current['classes'] = []

        current['classes'].append(to_parse.match_group(1))

        current['conditions'].append({ 'op': 'has_tag', 'key': '.' + to_parse.match_group(1) })

# parse zoom level
    if to_parse.match('\|z([0-9]*)(-?)([0-9]*)'):
        if to_parse.match_group(1):
            current['max_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(1)) - 1)

        if to_parse.match_group(1) and not to_parse.match_group(2):
            current['min_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(1)))

        if to_parse.match_group(3):
            current['min_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(3)))

# parse conditions - TODO
    while to_parse.match('\['):
        result = parse_condition(to_parse)
        if result:
            current['conditions'].append(result)

# parse pseudo classes
    while to_parse.match(':([a-zA-Z0-9_]+)'):
        if 'pseudo_classes' in current:
            pass
        else:
            current['pseudo_classes'] = []

        current['pseudo_classes'].append(to_parse.match_group(1))

# parse pseudo element
    while to_parse.match('::(\(?)([a-zA-Z0-9_\*\-]+)(\)?)'):
        if to_parse.match_group(1) and to_parse.match_group(3):
            current['create_pseudo_element'] = False

        current['pseudo_element'] = to_parse.match_group(2)

    return current

def parse_selectors(selectors, to_parse):
    while True:
        selector = {}
        selectors.append(selector)

        sel1 = parse_selector_part(to_parse)
        sel2 = None
        sel3 = None

        try:
            sel2 = parse_selector_part(to_parse, '>|<|near')
        except ParseError:
            pass

        try:
            sel3 = parse_selector_part(to_parse)
        except ParseError:
            if sel2: # if a link selector exists we need a 3rd selector
                raise

        if sel1 and sel2 and sel3:
            selector['parent_selector'] = sel1
            selector['link_selector'] = sel2
            selector['selector'] = sel3

        elif sel1 and not sel2 and sel3:
            selector['parent_selector'] = sel1
            selector['link_selector'] = {
                'type': '',
                'conditions': []
            }
            selector['selector'] = sel3

        else:
            selector['selector'] = sel1

        if not to_parse.match('\s*,'):
          return
