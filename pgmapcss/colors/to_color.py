def to_color(value):
    import re
    if re.match('#[a-fA-F0-9]{6,8}', value):
        return value

    if re.match('#[a-fA-F0-9]{3,4}', value):
        r = '#'
        for i in range(1, len(value)):
            r += value[i] + value[i]

        return r

    return None

def check_color(value):
    ret = to_color(value)

    if ret is None:
        debug("Warning: Unknown color '{}'".format(value))

    return ret
