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
    sdec_level = [']']
    level = 0
    pretty = ''
    i = iter(json.dumps(raw))
    for ch in i:
        if ch in inc_level:
            level += 1
            pretty += ch
            pretty += '\n' + ' '*level
        elif ch in dec_level:
            level -=1
            pretty += '\n' + ' '*level
            pretty += ch
        elif ch in sdec_level:
            ch+=next(i)
            level -=1
            pretty += ch
            pretty += '\n' + ' '*level
        else:
            pretty += ch
    return pretty

def pretty_json(raw: dict, indent=2) -> str:
    'Returns an auto-indented/pretty JSON string'
    return __inc(raw, indent)


tests = [
    (
        ({ 'a': [1,2,3], 'b': { 'c': { 'd': [5,5,5] } }, 'z': 'hello world' }, 2),
        '{\n  "a": [1,2,3],\n  "b": {\n    "c": {\n      "d": [5,5,5],\n    }\n  },\n  "z": "hello world"\n}',
    ),
    (
        ({ 'a': [1,2,3], 'b': { 'c': { 'd': [5,5,5] } }, 'z': 'hello world' }, 4),
        '{\n    "a": [1,2,3],\n    "b": {\n        "c": {\n            "d": [5,5,5],\n        }\n    },\n    "z": "hello world"\n}',
    ),
]

for i, ((data, indent), expected) in enumerate(tests):
    print(i, expected, sep='\n')

for (data, indent), expected in tests:
    result = pretty_json(data, indent)
    assert result == expected, f'{result} != {expected}'
