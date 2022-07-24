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
    def __init__(self, words, prefix_length=2):
        self.words = set(words)
        self.mappings = set()
        self.prefix_length = prefix_length
        if self.prefix_length:
            for word in self.words:
                self.mappings.add(tuple(word[:self.prefix_length]))
        self.i = 0

    def solve(self, puzzle: str):
        seen = []
        if self.prefix_length:
            options = self.headify(puzzle, n=self.prefix_length, mappings=self.mappings)
        else:
            options = permutations(puzzle)

        for i, possible in enumerate(options):
            if ''.join(possible) in self.words:
                result = ''.join(possible)
                if result not in seen:
                    yield result
                    seen.append(result)
        self.i = i

    def headify(self, s, n=1, mappings=[]):
        s = list(s)
        for head in permutations(s, n):
            if mappings and head not in mappings:
                continue
            pool = copy(s)
            for el in head:
                # print(el, pool)
                pool.remove(el)
            for p in permutations(pool):
                yield *head, *p


def test(puzzle):
    n = len(puzzle)
    print('-->\n', n, puzzle)

    s = MySolver(get_words(n), prefix_length=0)
    start = time.time()
    result = list(s.solve(puzzle))
    print(f'{time.time()-start:.05f}, ', 'total:', s.i, ', prefix len:', s.prefix_length, ', ', result)

    for pl in [2,3,4,5,6,7]:
        s = MySolver(get_words(n), prefix_length=pl)
        start = time.time()
        result = list(s.solve(puzzle))
        print(f'{time.time()-start:.05f}, ', 'total:', s.i, ', prefix len:', s.prefix_length, ', ', result)

words = [
    'appealign',
    'ayahausca',
    'residents',
]

for w in words:
    test(w)


#  ☯ ~/d/s/i/lesson09_word_target python3 solution.py
# -->
#  9 appealign
# 0.05662,  total: 362879 , prefix len: 0 ,  ['appealing', 'panplegia', 'lagniappe']
# 0.07152,  total: 287279 , prefix len: 2 ,  ['appealing', 'panplegia', 'lagniappe']
# 0.04630,  total: 179999 , prefix len: 3 ,  ['appealing', 'panplegia', 'lagniappe']
# 0.01518,  total: 57839 , prefix len: 4 ,  ['appealing', 'panplegia', 'lagniappe']
# 0.00419,  total: 9263 , prefix len: 5 ,  ['appealing', 'panplegia', 'lagniappe']
# 0.00511,  total: 887 , prefix len: 6 ,  ['appealing', 'panplegia', 'lagniappe']
# 0.01213,  total: 75 , prefix len: 7 ,  ['appealing', 'panplegia', 'lagniappe']
# -->
#  9 ayahausca
# 0.05414,  total: 362879 , prefix len: 0 ,  ['ayahausca', 'ayahuasca']
# 0.07468,  total: 302399 , prefix len: 2 ,  ['ayahausca', 'ayahuasca']
# 0.03674,  total: 147599 , prefix len: 3 ,  ['ayahausca', 'ayahuasca']
# 0.00498,  total: 19199 , prefix len: 4 ,  ['ayahausca', 'ayahuasca']
# 0.00149,  total: 2207 , prefix len: 5 ,  ['ayahausca', 'ayahuasca']
# 0.00345,  total: 287 , prefix len: 6 ,  ['ayahausca', 'ayahuasca']
# 0.01120,  total: 95 , prefix len: 7 ,  ['ayahausca', 'ayahuasca']
# -->
#  9 residents
# 0.05310,  total: 362879 , prefix len: 0 ,  ['residents', 'dissenter', 'triedness', 'tiredness']
# 0.06476,  total: 251999 , prefix len: 2 ,  ['residents', 'dissenter', 'triedness', 'tiredness']
# 0.04216,  total: 166319 , prefix len: 3 ,  ['residents', 'dissenter', 'triedness', 'tiredness']
# 0.01422,  total: 54599 , prefix len: 4 ,  ['residents', 'dissenter', 'triedness', 'tiredness']
# 0.00481,  total: 12983 , prefix len: 5 ,  ['residents', 'dissenter', 'triedness', 'tiredness']
# 0.00448,  total: 1871 , prefix len: 6 ,  ['residents', 'dissenter', 'triedness', 'tiredness']
# 0.01152,  total: 263 , prefix len: 7 ,  ['residents', 'dissenter', 'triedness', 'tiredness']
