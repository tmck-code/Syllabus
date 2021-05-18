#!/usr/bin/env python3
import json
from glob import glob
from itertools import zip_longest

def __group_by_n(items, n):
    for group in zip_longest(*[iter(items)]*n):
        yield list(filter(None.__ne__, group))

def __rec(raw: dict, indent=2, level=0) -> str:
    print('up to', level, raw)
    for k, v in raw.items():
        if isinstance(v, dict):
            return __rec(v, indent, level+1)

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

# for i, ((data, indent), expected) in enumerate(tests):
#     print(i, expected, sep='\n')

for (data, indent), expected in tests:
    result = pretty_json(data, indent)
    print('result\n', result)
    print('expected\n', expected)
    for l1, l2 in zip(expected.split('\n'), result.split('\n')):
        assert l1 == l2, f'{l1} != {l2}'
    assert result == expected, f'{result} != {expected}'
