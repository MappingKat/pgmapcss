from pkg_resources import *
from ..includes import *
from .base import config_base

class Functions:
    def __init__(self):
        self.eval_functions = None
        self.eval_functions_source = {}
        self._eval = None

    def list(self):
        if not self.eval_functions:
            self.resolve_config()

        return self.eval_functions

    def print(self, indent=''):
        ret = ''

        for func, src in self.eval_functions_source.items():
            ret += src

        # indent all lines
        ret = indent + ret.replace('\n', '\n' + indent)

        return ret


    def eval(self, statement):
        if not self._eval:
            content = \
                'def _eval(statement):\n' +\
                '    import re\n' +\
                '    ' + resource_string(__name__, 'base.py').decode('utf-8').replace('\n', '\n    ') +\
                '\n' +\
                '    ' + include_text().replace('\n', '\n    ') +\
                '\n' +\
                self.print(indent='    ') + '\n'\
                '    return eval(statement)'

            eval_code = compile(content, '<eval functions>', 'exec')
            eval_ns = {}
            exec(eval_code, eval_ns, eval_ns);
            self._eval = eval_ns['_eval']

        return self._eval(statement)

    def resolve_config(self):
        exec(
            resource_string(__name__, 'base.py').decode('utf-8') +
            self.print()
        )

        self.eval_functions = {}
        for func, src in self.eval_functions_source.items():
            if 'config_eval_' + func in locals():
                config = locals()['config_eval_' + func](func)
            else:
                config = config_base(func)

            if config.op is None:
                config.op = set()
            elif type(config.op) == tuple:
                config.op = set( config.op )
            else:
                config.op = { config.op }

            self.eval_functions[func] = config

    def register(self, func, src):
        self.eval_functions_source[func] = src

    def call(self, func, param, stat):
        import re
        import pgmapcss.db as db
        config = self.eval_functions[func]

        statement = config.compiler([ repr(p) for p in param ], '', stat)
        return self.eval(statement)

    def test(self, func, src):
        print('* Testing %s' % func)

        import re
        import pgmapcss.db as db
        rows = src.split('\n')
        config = self.eval_functions[func]

        ret = '''
create or replace function __eval_test__() returns text
as $body$
import re
''' +\
resource_string(__name__, 'base.py').decode('utf-8') +\
include_text() +\
'''
current = { 'object': { 'id': 'n123', 'tags': { 'amenity': 'restaurant', 'name': 'Foobar', 'cuisine': 'pizza;kebab;noodles' }}, 'pseudo_element': 'default', 'pseudo_elements': ['default', 'test'], 'tags': { 'amenity': 'restaurant', 'name': 'Foobar', 'cuisine': 'pizza;kebab;noodles' }, 'properties': { 'default': { 'width': '2', 'color': '#ff0000' }, 'test': { 'fill-color': '#00ff00' } } }
render_context = {'bbox': '010300002031BF0D000100000005000000DBF1839BB5DC3B41E708549B2B705741DBF1839BB5DC3B41118E9739B171574182069214CCE23B41118E9739B171574182069214CCE23B41E708549B2B705741DBF1839BB5DC3B41E708549B2B705741', 'scale_denominator': 8536.77}
'''
        ret += self.print()
        ret += "result = ''\n"

        param_in = None
        for r in rows:
            m = re.match('# IN (.*)$', r)
            if m:
                param_in = eval(m.group(1))

            m = re.match('# OUT (.*)$', r)
            if m:
                return_out = eval(m.group(1))

                ret += 'ret = ' + config.compiler([ repr(p) for p in param_in ], '', {}) + '\n'
                ret += 'result += "IN  %s\\n"\n' % repr(param_in)
                ret += 'result += "EXP %s\\n"\n' % repr(return_out)
                ret += 'result += "OUT %s\\n" % repr(ret)\n'

                ret += 'if type(ret) != str:\n    result += "ERROR not a string: " + repr(ret) + "\\n"\n'
                ret += 'elif ret != %s:\n    result += "ERROR return value wrong!\\n"\n' % repr(return_out)

        ret += 'return result\n'
        ret += "$body$ language 'plpython3u' immutable;"
        #print(ret)
        conn = db.connection()
        conn.execute(ret)

        r = conn.prepare('select __eval_test__()');
        res = r()[0][0]

        print(res)

        if(re.search("^ERROR", res, re.MULTILINE)):
            raise Exception("eval-test failed!")

    def test_all(self):
        if not self.eval_functions:
            self.resolve_config()

        [ self.test(func, src) for func, src in self.eval_functions_source.items() ]
