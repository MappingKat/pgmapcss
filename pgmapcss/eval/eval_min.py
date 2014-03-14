class config_eval_min(config_base):
    def mutable(self, param_values, stat):
        import pgmapcss.eval
        config_metric = pgmapcss.eval.eval_functions.list()['metric']
        ret = [ config_metric.mutable([p], stat) for p in param_values ]
        return min(ret)

def eval_min(param):
    if len(param) == 0:
        return ''
    if len(param) == 1:
        param = param[0].split(';')

    values = [ eval_metric([v]) for v in param ]
    values = [ float(v) for v in values if v != '' ]

    while '' in values:
        values.remove('')
    if len(values) == 0:
        return ''

    return float_to_str(min(values))

# TESTS
# IN ['1.0', '5', '3']
# OUT '1'
# IN ['1.0', '']
# OUT '1'
# IN ['1;4;5']
# OUT '1'
# IN ['1px;1000m']
# OUT '1'
# IN []
# OUT ''
# IN ['1;;5']
# OUT '1'
# IN ['']
# OUT ''
