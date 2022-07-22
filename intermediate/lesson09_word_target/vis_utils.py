import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalTrueColorFormatter

from IPython.display import JSON
from IPython.core.display_functions import display

def ppd(d, indent=2):
    'pretty-prints a dict'
    print(highlight(
        code      = json.dumps(d, indent=indent, default=list),
        lexer     = JsonLexer(),
        formatter = TerminalTrueColorFormatter(style='material')
    ).strip())

def ppj(j, indent=2):
    'pretty-prints a JSON string'
    ppd(json.loads(j), indent=indent)