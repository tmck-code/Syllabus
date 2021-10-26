#!/usr/bin/env python3
import json
from glob import glob
from itertools import zip_longest
from dataclasses import dataclass

def inc(raw: dict, indent=2) -> str:
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

import re

def flatten_then_indent(raw: dict, indent=2) -> str:
    ops = [
        (r'(^{)',     r'\1\n'),
        (r'(}$)',     r'\n\1'),
        (r'(},)( )',  r'\n\1\n'),
        (r'(],)( )',  r'\1\n'),
        (r'(: {)',    r'\1\n'),
        (r'(\])(})',  r'\1\n\2'),
        (r'(\})(}|$)',  r'\n\1\n\2'),
    ]
    s = json.dumps(raw)
    for pattern, substitution in ops:
        s = re.sub(pattern, substitution, s)
    level = 0
    ss = []
    for line in map(str.strip, s.split('\n')):
        if re.search(r'}$|},$|(}|\])\]$', line):
            level -= 1
            ss += [' '*(level*indent) + line]
            continue
        ss += [' '*(level*indent) + line]
        if re.search(r': {|^{$|\[$', line):
            level += 1
    print(ss)
    return '\n'.join(ss).replace(', ', ',').strip()

@dataclass
class SlidingWindow:
    obj: str
    window_size: int = 3

    def __iter__(self):
        for i in range(0, len(self.obj)):
            yield self.obj[i:i+self.window_size]

def slide(raw: dict, indent=2) -> str:
    level=0
    ind = ' '*indent
    w = SlidingWindow(json.dumps(raw)).__iter__()
    print_space = True
    fmt = ''
    while True:
        try:
            i = next(w)
        except StopIteration:
            break
        if i.startswith(' '):
            if print_space:
                fmt += ' '
            print_space = True
        elif i.startswith('{'):
            fmt += i[0]+'\n'
            level += 1
            fmt += level*ind
        elif i.startswith('['):
            level += 1
            fmt += i[0]+'\n'+level*ind
        elif i.startswith((']', '}')):
            level -= 1
            fmt += '\n'+level*ind+i[0]
        elif i.startswith(','):
            fmt += i[0]+'\n'+level*ind
            if i[1] == ' ':
                print_space = False
        else:
            fmt += i[0]
    return fmt

from __future__ import annotations

# -------------
# {
#   "a": "b"
# }
# -------------
# {
#   [
#     1
#   ]
# }
# 

from collections import namedtuple

BracketPair = namedtuple('BracketPair', ['left', 'right'])

@dataclass
class GroupMember:
    value: object

    def repr(self):
        return str(self.value)

@dataclass
class IndentGroup:
    children: list
    brackets: BracketPair
    indent: int = 4 * ' '

    def repr(self):
        fmt = self.brackets.left
        for ch in self.children:
            if isinstance(ch, IndentGroup):
                fmt += ch.repr()
            elif isinstance(ch, GroupMember):
                fmt += self.indent
        return fmt

@dataclass
class IndentGroup:
    children: list
    brackets: BracketPair
    indent: int = 4 * ' '

    def repr(self):
        fmt = self.brackets.left
        for ch in self.children:
            if isinstance(ch, (list, dict)):
                fmt += ch.repr()
            elif isinstance(ch, GroupMember):
                fmt += self.indent
        return fmt




tests = [
    (
        ({ 'a': [1,2,3], 'b': { 'c': { 'd': [5,5,5] } }, 'z': 'hello world' }, 2),
'''{
  "a": [
    1,
    2,
    3
  ],
  "b": {
    "c": {
      "d": [
        5,
        5,
        5
      ]
    }
  },
  "z": "hello world"
}'''
    ),
    (
        ({ 'a': [1,2,3], 'b': { 'c': { 'd': [5,5,5] } }, 'z': 'hello world' }, 4),
'''{
    "a": [
        1,
        2,
        3
    ],
    "b": {
        "c": {
            "d": [
                5,
                5,
                5
            ]
        }
    },
    "z": "hello world"
}'''
    ),
    (
        ({ "_outer": { "a": [1,2,3], "b": { "c": { "d": [5,5,5] } }, "z": "hello world" } }, 2),
        '''\
{
  "_outer": {
    "a": [
      1,
      2,
      3
    ],
    "b": {
      "c": {
        "d": [
          5,
          5,
          5
        ]
      }
    },
    "z": "hello world"
  }
}'''
    ),
]

def run_test():
    for (data, indent), expected in tests:
        # result = inc(data, indent)
        # result = flatten_then_indent(data, indent)
        result = slide(data, indent)
        print('-----', 'expected', expected,'result', result, sep='\n')
        for l1, l2 in zip(expected.split('\n'), result.split('\n')):
            assert l1 == l2, [l1, l2]
        assert result == expected, f'{result} != {expected}'



if __name__ == '__main__':
    run_test()
