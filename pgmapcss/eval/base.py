def to_float(v, default=None):
    try:
        return float(v)
    except ValueError:
        return default
def to_int(v, default=None):
    try:
        return int(v)
    except ValueError:
        return default
def float_to_str(v, default=None):
    r = repr(v)
    if r[-2:] == '.0':
        r = r[:-2]
    return r
def debug(text):
    plpy.notice(text)

class config_base:
    math_level = None
    op = None
    unary = False

    def __init__(self, func):
        import re

        if not re.match('[a-zA-Z_0-9]+$', func):
            raise Exception('Illegal eval function name: ' + func)

        self.func = func

    def compiler(self, param, eval_param, stat):
        return 'eval_' + self.func + '([' + ', '.join(param) + ']' + eval_param + ')'

    def __call__(self, param, stat):
        try:
            current
        except NameError:
            import pgmapcss.eval
            return pgmapcss.eval.eval_functions.call(self.func, param, stat)
        else:
            return eval(self.compiler(param, '', {}))
