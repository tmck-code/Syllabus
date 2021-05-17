#!/usr/bin/env python3
import json

def pretty_json(raw: dict, indent=2) -> str:
    'Returns an auto-indented/pretty JSON string'

tests = [
    (
        ({ 'a': [1,2,3], 'b': { 'c': { 'd': [5,5,5], } }, 'z': 'hello world' }, 2),
        '{\n  "a": [1,2,3],\n  "b": {\n    "c": {\n      "d": [5,5,5],\n    }\n  },\n  "z": "hello world"\n}',
    ),
    (
        ({ 'a': [1,2,3], 'b': { 'c': { 'd': [5,5,5], } }, 'z': 'hello world' }, 4),
        '{\n    "a": [1,2,3],\n    "b": {\n        "c": {\n            "d": [5,5,5],\n        }\n    },\n    "z": "hello world"\n}',
    ),
]

for (data, indent), expected in tests:
    result = pretty_json(data, indent)
    assert result == expected, f'{result} != {expected}'
