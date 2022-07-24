#!/usr/bin/env python3

import urllib.request
from dataclasses import dataclass
from copy import copy
import time
from itertools import permutations

def get_words(n=9):
    urllib.request.urlretrieve("https://github.com/dwyl/english-words/raw/master/words_alpha.txt", "words_alpha.txt")
    with open('words_alpha.txt', 'r') as istream:
        for line in map(str.strip, istream):
            if len(line) == n:
                yield line

class Solver:
    def __init__(self, words):
        pass

    def solve(self, puzzle: str) -> str:
        pass

class MySolver(Solver):
    def __init__(self, words, use_mapping=True):
        self.words = set(words)
        self.mappings = set()
        self.use_mapping = use_mapping
        if use_mapping:
            for word in self.words:
                self.mappings.add(tuple(word[:2]))

    def solve(self, puzzle: str):
        seen = []
        if self.use_mapping:
            options = self.headify(puzzle, n=2, mappings=self.mappings)
        else:
            options = permutations(puzzle)

        for i, possible in enumerate(options):
            if ''.join(possible) in self.words:
                result = ''.join(possible)
                if result not in seen:
                    yield result
                    seen.append(result)
        print('total:', i)

    def headify(self, s, n=1, mappings=[]):
        s = list(s)
        for head in permutations(s, n):
            if self.use_mapping and head not in mappings:
                continue
            pool = copy(s)
            for el in head:
                # print(el, pool)
                pool.remove(el)
            for p in permutations(pool):
                yield *head, *p


def test(puzzle):
    n = len(puzzle)
    print('->', n, puzzle)

    s = MySolver(get_words(n))
    start = time.time()
    print(list(s.solve(puzzle)))
    print(f'{time.time()-start:.05f}')

    s = MySolver(get_words(n), use_mapping=False)
    start = time.time()
    print(list(s.solve(puzzle)))
    print(f'{time.time()-start:.05f}')

words = [
    'appealign',
    'ayahausca',
    'residents',
]

for w in words:
    test(w)
