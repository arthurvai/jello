"""jello - query JSON at the command line with python syntax"""

import os
import sys
import ast
import json
from jello.dotmap import DotMap
from jello.options import opts, JelloTheme


schema_list = []


color_map = {
    'black': ('ansiblack', '\33[30m'),
    'red': ('ansired', '\33[31m'),
    'green': ('ansigreen', '\33[32m'),
    'yellow': ('ansiyellow', '\33[33m'),
    'blue': ('ansiblue', '\33[34m'),
    'magenta': ('ansimagenta', '\33[35m'),
    'cyan': ('ansicyan', '\33[36m'),
    'gray': ('ansigray', '\33[37m'),
    'brightblack': ('ansibrightblack', '\33[90m'),
    'brightred': ('ansibrightred', '\33[91m'),
    'brightgreen': ('ansibrightgreen', '\33[92m'),
    'brightyellow': ('ansibrightyellow', '\33[93m'),
    'brightblue': ('ansibrightblue', '\33[94m'),
    'brightmagenta': ('ansibrightmagenta', '\33[95m'),
    'brightcyan': ('ansibrightcyan', '\33[96m'),
    'white': ('ansiwhite', '\33[97m'),
}


def set_env_colors():
    """
    This function does not return a value. It just updates the JelloTheme.colors dictionary.

    Grab custom colors from JELLO_COLORS environment variable and .jelloconf.py file. Individual colors from JELLO_COLORS
    take precedence over .jelloconf.py. Individual colors from JELLO_COLORS will fall back to .jelloconf.py or default
    if the env variable color is set to 'default'

    JELLO_COLORS env variable takes 6 comma separated string values and should be in the format of:

    JELLO_COLORS=<keyname_color>,<keyword_color>,<number_color>,<string_color>,<arrayid_color>,<arraybracket_color>

    Where colors are: black, red, green, yellow, blue, magenta, cyan, gray, brightblack, brightred,
                      brightgreen, brightyellow, brightblue, brightmagenta, brightcyan, white, default

    Default colors:

    JELLO_COLORS=blue,brightblack,magenta,green,red,magenta
    or
    JELLO_COLORS=default,default,default,default,default,default

    """
    env_colors = os.getenv('JELLO_COLORS')
    input_error = False

    if env_colors:
        color_list = env_colors.split(',')

    if env_colors and len(color_list) != 6:
        input_error = True

    if env_colors:
        for color in color_list:
            if color not in ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'gray', 'brightblack', 'brightred',
                             'brightgreen', 'brightyellow', 'brightblue', 'brightmagenta', 'brightcyan', 'white', 'default']:
                input_error = True
    else:
        color_list = ['default', 'default', 'default', 'default', 'default', 'default']

    # if there is an issue with the env variable, just set all colors to default and move on
    if input_error:
        print('jello:   Warning: could not parse JELLO_COLORS environment variable\n', file=sys.stderr)
        color_list = ['default', 'default', 'default', 'default', 'default', 'default']

    # Try the color set in the JELLO_COLORS env variable first. If it is set to default, then fall back to .jelloconf.py
    # configuration. If nothing is set in jelloconf.py, then use the default colors.
    JelloTheme.colors = {
        'key_name': color_map[color_list[0]] if not color_list[0] == 'default' else color_map[opts.keyname_color] if opts.keyname_color else color_map['blue'],
        'keyword': color_map[color_list[1]] if not color_list[1] == 'default' else color_map[opts.keyword_color] if opts.keyword_color else color_map['brightblack'],
        'number': color_map[color_list[2]] if not color_list[2] == 'default' else color_map[opts.number_color] if opts.number_color else color_map['magenta'],
        'string': color_map[color_list[3]] if not color_list[3] == 'default' else color_map[opts.string_color] if opts.string_color else color_map['green'],
        'array_id': color_map[color_list[4]] if not color_list[4] == 'default' else color_map[opts.arrayid_color] if opts.arrayid_color else color_map['red'],
        'array_bracket': color_map[color_list[5]] if not color_list[5] == 'default' else color_map[opts.arraybracket_color] if opts.arraybracket_color else color_map['magenta']
    }


def load_json(data):
    try:
        json_dict = json.loads(data)
    except Exception:
        # if json.loads fails, assume the data is json lines and parse
        json_dict = [json.loads(i) for i in data.splitlines()]

    return json_dict


def create_schema(src, path=''):
    """
    Creates a grep-able schema representation of the JSON.

    This function is recursive, so output is stored within the schema_list list. Make sure to
    initialize schema_list to a blank list and set colors by calling set_env_colors() before
    calling this function.
    """
    if not opts.mono:
        CEND = '\33[0m'
        CBOLD = '\33[1m'
        CKEYNAME = f'{JelloTheme.colors["key_name"][1]}'
        CKEYWORD = f'{JelloTheme.colors["keyword"][1]}'
        CNUMBER = f'{JelloTheme.colors["number"][1]}'
        CSTRING = f'{JelloTheme.colors["string"][1]}'
        CARRAYID = f'{JelloTheme.colors["array_id"][1]}'
        CARRAYBRACKET = f'{JelloTheme.colors["array_bracket"][1]}'

    else:
        CEND = ''
        CBOLD = ''
        CKEYNAME = ''
        CKEYWORD = ''
        CNUMBER = ''
        CSTRING = ''
        CARRAYID = ''
        CARRAYBRACKET = ''

    if isinstance(src, list) and path == '':
        for i, item in enumerate(src):
            create_schema(item, path=f'.{CARRAYBRACKET}[{CEND}{CARRAYID}{i}{CEND}{CARRAYBRACKET}]{CEND}')

    elif isinstance(src, list):
        for i, item in enumerate(src):
            create_schema(item, path=f'{path}.{CBOLD}{CKEYNAME}{src}{CEND}{CARRAYBRACKET}[{CEND}{CARRAYID}{i}{CEND}{CARRAYBRACKET}]{CEND}')

    elif isinstance(src, dict):
        for k, v in src.items():
            if isinstance(v, list):
                for i, item in enumerate(v):
                    create_schema(item, path=f'{path}.{CBOLD}{CKEYNAME}{k}{CEND}{CARRAYBRACKET}[{CEND}{CARRAYID}{i}{CEND}{CARRAYBRACKET}]{CEND}')

            elif isinstance(v, dict):
                if not opts.mono:
                    k = f'{CBOLD}{CKEYNAME}{k}{CEND}'
                create_schema(v, path=f'{path}.{k}')

            else:
                k = f'{CBOLD}{CKEYNAME}{k}{CEND}'
                val = json.dumps(v, ensure_ascii=False)
                if val == 'true' or val == 'false' or val == 'null':
                    val = f'{CKEYWORD}{val}{CEND}'
                elif val.replace('.', '', 1).isdigit():
                    val = f'{CNUMBER}{val}{CEND}'
                else:
                    val = f'{CSTRING}{val}{CEND}'

                schema_list.append(f'{path}.{k} = {val};')

    else:
        val = json.dumps(src, ensure_ascii=False)
        if val == 'true' or val == 'false' or val == 'null':
            val = f'{CKEYWORD}{val}{CEND}'
        elif val.replace('.', '', 1).isdigit():
            val = f'{CNUMBER}{val}{CEND}'
        else:
            val = f'{CSTRING}{val}{CEND}'

        path = path or '.'

        schema_list.append(f'{path} = {val};')


def create_json(data):
    separators = None
    indent = 2

    if opts.compact or opts.lines:
        separators = (',', ':')
        indent = None

    if isinstance(data, dict):
        return json.dumps(data, separators=separators, indent=indent, ensure_ascii=False)

    if isinstance(data, list):
        if not opts.lines:
            return json.dumps(data, separators=separators, indent=indent, ensure_ascii=False)

        # check if this list includes lists
        list_includes_list = False
        for item in data:
            if isinstance(item, list):
                list_includes_list = True
                break

        if opts.lines and list_includes_list:
            raise ValueError('Cannot print list of lists as lines. Try normal JSON output.')

        # print lines for a flat list
        else:
            flat_list = ''
            for entry in data:
                if entry is None:
                    if opts.nulls:
                        flat_list += 'null\n'
                    else:
                        flat_list += '\n'

                elif isinstance(entry, (dict, bool, int, float)):
                    flat_list += json.dumps(entry, separators=separators, ensure_ascii=False) + '\n'

                elif isinstance(entry, str):
                    # replace \n with \\n here so lines with newlines literally print the \n char
                    entry = entry.replace('\n', '\\n')
                    if opts.raw:
                        flat_list += f'{entry}' + '\n'
                    else:
                        flat_list += f'"{entry}"' + '\n'

            return flat_list.rstrip()

    # naked single item return case
    elif data is None:
        if opts.nulls:
            return 'null'
        else:
            return ''

    elif isinstance(data, (bool, int, float)):
        return json.dumps(data, ensure_ascii=False)

    elif isinstance(data, str):
        # replace \n with \\n here so lines with newlines literally print the \n char
        data = data.replace('\n', '\\n')
        if opts.raw:
            return f'{data}'
        else:
            return f'"{data}"'

    # only non-serializable types are left. Force an exception from json.dumps()
    else:
        json.dumps(data)
        # this code should not run, but just in case something slips by above
        raise TypeError(f'Object is not JSON serializable')


def pyquery(data, query):
    # if data is a list of dictionaries, then need to iterate through and convert all dictionaries to DotMap
    if isinstance(data, list):
        _ = [DotMap(i, _dynamic=False, _prevent_method_masking=True) if isinstance(i, dict)
             else i for i in data]

    elif isinstance(data, dict):
        _ = DotMap(data, _dynamic=False, _prevent_method_masking=True)

    else:
        _ = data

    jelloconf = ''
    conf_file = ''

    if opts.initialize:
        if sys.platform.startswith('win32'):
            conf_file = os.path.join(os.environ['APPDATA'], '.jelloconf.py')
        else:
            conf_file = os.path.join(os.environ["HOME"], '.jelloconf.py')

        try:
            with open(conf_file, 'r') as f:
                jelloconf = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f'-i used and initialization file not found: {conf_file}')

    query = jelloconf + query
    output = None

    # extract jello options from .jelloconf.py (compact, raw, lines, nulls, mono, and custom colors)
    for expr in ast.parse(jelloconf).body:
        if isinstance(expr, ast.Assign):
            if expr.targets[0].id == 'compact':
                opts.compact = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'raw':
                opts.raw = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'lines':
                opts.lines = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'nulls':
                opts.nulls = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'mono':
                opts.mono = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'schema':
                opts.schema = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'keyname_color':
                opts.keyname_color = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'keyword_color':
                opts.keyword_color = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'number_color':
                opts.number_color = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'string_color':
                opts.string_color = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'arrayid_color':
                opts.arrayid_color = eval(compile(ast.Expression(expr.value), '<string>', "eval"))
            if expr.targets[0].id == 'arraybracket_color':
                opts.arraybracket_color = eval(compile(ast.Expression(expr.value), '<string>', "eval"))

            # validate the data in the initialization file
            warn_options = False
            warn_colors = False

            for option in [opts.compact, opts.raw, opts.lines, opts.nulls, opts.mono, opts.schema]:
                if not isinstance(option, bool):
                    opts.compact = opts.raw = opts.lines = opts.nulls = opts.mono = opts.schema = None
                    warn_options = True

            for color_config in [opts.keyname_color, opts.keyword_color, opts.number_color,
                                 opts.string_color, opts.arrayid_color, opts.arraybracket_color]:
                valid_colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'gray', 'brightblack', 'brightred',
                                'brightgreen', 'brightyellow', 'brightblue', 'brightmagenta', 'brightcyan', 'white']
                if color_config not in valid_colors and color_config is not None:
                    opts.keyname_color = opts.keyword_color = opts.number_color = opts.string_color = opts.arrayid_color = opts.arraybracket_color = None
                    warn_colors = True

            if warn_options:
                print(f'Jello:   Warning: Options must be set to True or False in {conf_file}\n         Unsetting all options.\n')

            if warn_colors:
                valid_colors_string = ', '.join(valid_colors)
                print(f'Jello:   Warning: Colors must be set to one of: {valid_colors_string} in {conf_file}\n         Unsetting all colors.\n')

    # run the query
    block = ast.parse(query, mode='exec')
    last = ast.Expression(block.body.pop().value)    # assumes last node is an expression
    exec(compile(block, '<string>', mode='exec'))
    output = eval(compile(last, '<string>', mode='eval'))

    # convert output back to normal dict
    if isinstance(output, list):
        output = [i.toDict() if isinstance(i, DotMap) else i for i in output]

    elif isinstance(output, DotMap):
        output = output.toDict()

    # if DotMap returns a bound function then we know it was a reserved attribute name
    if hasattr(output, '__self__'):
        raise ValueError('Reserved key name. Use bracket notation to access this key.')

    return output


if __name__ == '__main__':
    main()
