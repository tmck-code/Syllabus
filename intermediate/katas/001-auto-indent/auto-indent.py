#!/usr/bin/env python3
import json
from glob import glob
from itertools import zip_longest

def __inc(raw: dict, indent=2) -> str:
    inc_level = {'{'}
    dec_level = {'}'}
    sdec_level = {'}', ']'}
    level = 0
    pretty = ''
    i = iter(json.dumps(raw))
    for ch in i:
        if ch == ',':
            ch2 = next(i)
            if ch2 == ' ':
                pretty += ','
                continue
        # Put the char, then newline & increase indent
        if ch in inc_level:
            level += indent
            pretty += ch
            pretty += '\n' + ' '*level
        # Put a newline & down a level, then put current char
        elif ch in dec_level:
            level -= indent
            pretty += '\n' + ' '*level
            pretty += ch
        # If we are at a ]
        elif ch in sdec_level:
            ch2=next(i)
            # Check if it's a comma next, i.e. "],"
            if ch2 == ',':
                # Then, put the "]," onto the current line, then newline, no
                # level change
                pretty += ch
                pretty += ch2
                pretty += '\n' + ' '*level
            # Otherwise, it's another level char like "]]" or "]}"
            else:
                # Put the current char, then newline & down a level for the next
                # level char
                pretty += ch
                level -= indent
                pretty += '\n' + ' '*level
                pretty += ch2
        else:
            pretty += ch
    return pretty + '\n'

def pretty_json(raw: dict, indent=2) -> str:
    'Returns an auto-indented/pretty JSON string'
    return __inc(raw, indent)


def __group_by_n(items, n):
    for group in zip_longest(*[iter(items)]*n):
        yield list(filter(None.__ne__, group))


import re

def flatten_then_indent(raw: dict, indent=2) -> str:
    ops = [
        (r'(^{)',     r'\1\n'),
        (r'(}$)',     r'\n\1'),
        (r'(},)( )',  r'\n\1\n'),
        (r'(],)( )',  r'\1\n'),
        (r'(: {)',    r'\1\n'),
        (r'(\])(})',  r'\1\n\2'),
    ]
    s = json.dumps(raw)
    for pattern, substitution in ops:
        s = re.sub(pattern, substitution, s)
    level = 0
    ss = []
    for line in s.split('\n'):
        if re.search(r'}$|},$|(}|\])\]$', line):
            level -= 1
            ss += [' '*(level*indent) + line]
            continue
        ss += [' '*(level*indent) + line]
        if re.search(r': {|^{$|\[$', line):
            level += 1
    return '\n'.join(ss).replace(', ', ',')


tests = [
    (
        ({ 'a': [1,2,3], 'b': { 'c': { 'd': [5,5,5] } }, 'z': 'hello world' }, 2),
        '{\n  "a": [1,2,3],\n  "b": {\n    "c": {\n      "d": [5,5,5]\n    }\n  },\n  "z": "hello world"\n}',
    ),
    (
        ({ 'a': [1,2,3], 'b': { 'c': { 'd': [5,5,5] } }, 'z': 'hello world' }, 4),
        '{\n    "a": [1,2,3],\n    "b": {\n        "c": {\n            "d": [5,5,5]\n        }\n    },\n    "z": "hello world"\n}',
    ),
]


for (data, indent), expected in tests:
    # result = pretty_json(data, indent)
    result = flatten_then_indent(data, indent)
    print('result', result, sep='\n')
    print('expected', expected, sep='\n')
    for l1, l2 in zip(expected.split('\n'), result.split('\n')):
        assert l1 == l2, [l1, l2]
    assert result == expected, f'{result} != {expected}'
