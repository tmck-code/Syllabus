import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalTrueColorFormatter

def ppj(j):
    print(highlight(j, JsonLexer(), TerminalTrueColorFormatter()))
   
def ppd(d, indent=2):
    ppj(json.dumps(d, indent=indent))
