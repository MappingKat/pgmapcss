from .compile_selector_part import compile_selector_part
from .compile_link_selector import compile_link_selector
from .compile_properties import compile_properties
from .compile_conditions import compile_conditions

def compile_statement(statement, stat, indent='    '):
    ret = ''
    object_selector = statement['selector']

    ret += indent + 'if (' + compile_selector_part(object_selector, stat) + '):\n'
    indent += '    '

    if 'link_selector' in statement:
        ret += indent + 'for parent_index, parent_object in enumerate(' + compile_link_selector(statement, stat) + '):\n'

        indent += '    '
        ret += indent + "current['parent_object'] = parent_object\n"
        ret += indent + "current['link_object'] = { 'tags': parent_object['link_tags'] }\n"
        ret += indent + "current['link_object']['tags']['index'] = str(parent_index)\n"
        ret += indent + 'if (' +\
          compile_conditions(statement['parent_selector']['conditions'], stat, "current['parent_object']['tags']") + ') and (' +\
          compile_conditions(statement['link_selector']['conditions'], stat, "current['link_object']['tags']") + '):\n'

        indent += '    '
        ret += indent + 'current[\'parent_object\'] = parent_object\n'

    # set current.pseudo_element_ind
    if object_selector['pseudo_element'] == '*':
        statement['current_pseudo_element'] = 'pseudo_element'
        ret += indent + "for pseudo_element in current['pseudo_elements']:\n"
        indent += '    '
        ret += indent + "current['pseudo_element'] = pseudo_element\n"
    else:
        statement['current_pseudo_element'] = repr(object_selector['pseudo_element'])
        ret += indent + "current['pseudo_element'] = " + statement['current_pseudo_element'] + '\n'

# TODO: prop_type
    ret += compile_properties(statement, stat, indent)

    if object_selector['pseudo_element'] == '*':
        indent = indent[4:]

    if 'link_selector' in statement:
        ret += indent + "current['parent_object'] = None\n"
        indent = indent[8:]

# create_pseudo_element
    if not 'create_pseudo_element' in object_selector or \
        object_selector['create_pseudo_element']:
        ret += indent + "current['has_pseudo_element'][" + statement['current_pseudo_element'] + '] = True\n'

    ret += '\n'

    return ret
