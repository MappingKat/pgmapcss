from .compile_statement import compile_statement
from .compile_eval import compile_eval
from .stat import *
import copy

def print_checks(prop, stat, main_prop=None, indent=''):
    ret = ''

    # @default_other
    if 'default_other' in stat['defines'] and prop in stat['defines']['default_other']:
        other = stat['defines']['default_other'][prop]['value']
        ret += indent + 'if not ' + repr(prop) + " in current['properties'][pseudo_element] or current['properties'][pseudo_element][" + repr(prop) + "] is None:\n"
        ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = current['properties'][pseudo_element][" + repr(other) + "] if " + repr(other) + " in current['properties'][pseudo_element] else None\n"

    # @values
    if 'values' in stat['defines'] and prop in stat['defines']['values']:
        values = stat['defines']['values'][prop]['value'].split(';')
        used_values = stat_property_values(prop, stat, include_illegal_values=True)

        # if there are used values which are not allowed, always check
        # resulting value and - if not allowed - replace by the first
        # allowed value
        if len([ v for v in used_values if not v in values ]):
            ret += indent + 'if ' + repr(prop) + " not in current['properties'][pseudo_element] or current['properties'][pseudo_element][" + repr(prop) + "] not in " + repr(values) + ":\n"
            ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = " + repr(values[0]) + '\n'

    return ret

def compile_function_check(statements, min_scale, max_scale, stat):
    replacement = {
      'style_id': stat['id'],
      'min_scale': min_scale,
      'max_scale': max_scale,
      'min_scale_esc': str(min_scale).replace('.', '_'),
      'pseudo_elements': repr(stat['pseudo_elements'])
    }

    ret = '''
def check_{min_scale_esc}(object):
# initialize variables
    global current
    current = {{
        'object': object,
        'pseudo_elements': {pseudo_elements},
        'tags': object['tags'],
        'types': object['types'],
        'properties': {{
            pseudo_element: {{ 'geo': object['geo'] }}
            for pseudo_element in {pseudo_elements}
         }},
        'has_pseudo_element': {{
            pseudo_element: False
            for pseudo_element in {pseudo_elements}
         }},
    }}

# All statements
'''.format(**replacement)

    for i in statements:
        # create a copy of the statement and modify min/max scale
        i = copy.deepcopy(i)
        i['selector']['min_scale'] = min_scale
        i['selector']['max_scale'] = max_scale

        ret += compile_statement(i, stat)

    ret += '''\
    # iterate over all pseudo-elements, sorted by 'object-z-index' if available
    for pseudo_element in sorted({pseudo_elements}, key=lambda s: to_float(current['properties'][s]['object-z-index'], 0.0) if 'object-z-index' in current['properties'][s] else 0):
        if current['has_pseudo_element'][pseudo_element]:
            current['pseudo_element'] = pseudo_element # for eval functions

            # Finally build return value(s)
            ret = {{
                'id': object['id'],
                'types': object['types'],
                'tags': current['tags'],
                'pseudo_element': pseudo_element
            }}

'''.format(**replacement)

    # handle @values, @default_other for all properties
    done_prop = []
    indent = '            '
    # start with props from @depend_property
    for main_prop, props in stat['defines']['depend_property'].items():
        props = props['value'].split(';')
        r = ''

        r += print_checks(main_prop, stat, indent=indent + '    ')
        done_prop.append(main_prop)

        for prop in props:
            r += print_checks(prop, stat, main_prop=main_prop, indent=indent + '    ')
            done_prop.append(prop)

        if r != '':
            ret += indent + 'if ' + repr(main_prop) + " in current['properties'][pseudo_element]:\n"
            ret += r

    for prop in [ prop for prop in stat_properties(stat) if not prop in done_prop ]:
        ret += print_checks(prop, stat, indent=indent)

    # postprocess requested properties (see @postprocess)
    for k, v in stat['defines']['postprocess'].items():
        ret += indent + "current['properties'][pseudo_element][" + repr(k) +\
               "] = " + compile_eval(v['value'], v, stat) + '\n'

    ret += '''\
            # set geo as return value AND remove key from properties
            ret['geo'] = current['properties'][pseudo_element].pop('geo');
            ret['properties'] = current['properties'][pseudo_element]
            yield(( 'result', ret))
'''.format(**replacement)

    return ret
