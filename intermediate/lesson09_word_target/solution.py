#!/usr/bin/env python3

import urllib.request
from dataclasses import dataclass

def get_words():
    urllib.request.urlretrieve("https://github.com/dwyl/english-words/raw/master/words_alpha.txt", "words_alpha.txt")
    with open('words_alpha.txt', 'r') as istream:
        for line in map(str.strip, istream):
            if len(line) == 9:
                yield line

def permutations(iterable, r=None, mapping=[]):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210

    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))

    option = tuple(pool[i] for i in indices[:r])

    if mapping:
        for m in mapping:
            # print('->', m, option, option[:len(m)])
            if m == option[:len(m)]:
                # print('✓', option)
                yield option
    else:
        yield option

    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                option = tuple(pool[i] for i in indices[:r])
                # print('->', option)

                if mapping:
                    for m in mapping:
                        # print('->', m, option, option[:len(m)])
                        if m == option[:len(m)]:
                            # print('✓', option)
                            yield option
                else:
                    yield option
                break
        else:
            return

class Solver:
    def __init__(self, words):
        pass

    def solve(self, puzzle: str) -> str:
        pass

class MySolver(Solver):
    def __init__(self, words):
        self.words = set(words)
        self.mappings = set()
        for word in self.words:
            self.mappings.add(tuple(word[:2]))

    def solve(self, puzzle: str):
        seen = []
        options = list(permutations(puzzle.lower(), r=9, mapping=list(self.mappings)))
        # options = list(permutations(puzzle.lower(), r=9))
        # print('->', len(options), options)
        for possible in options:
            if ''.join(possible) in self.words:
                result = ''.join(possible)
                if result not in seen:
                    yield result
                    seen.append(result)

s = MySolver(get_words())
print(list(s.solve('appealign')))
