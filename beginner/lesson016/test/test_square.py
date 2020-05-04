import pytest
import os, sys

for path in ['../']:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), path)))

import grid, shapes

class TestSquare:

    PIXEL_STATES = grid.PixelStates('▣', '-')

    def test_filled_square(self):
        result = str(shapes.FilledSquare(10, 10, 2, TestSquare.PIXEL_STATES))
        expected = '''\
     0 1 2 3 4 5 6 7 8 9 10 11 12 13
0    - - - - - - - - - - - - - -
1    - - - - - - - - - - - - - -
2    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
3    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
4    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
5    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
6    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
7    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
8    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
9    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
10   - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
11   - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
12   - - - - - - - - - - - - - -
13   - - - - - - - - - - - - - -'''

        assert expected == result, f'expected {expected} != result {result}'


    def test_hollow_square(self):
        result = str(shapes.HollowSquare(10, 10, 2, TestSquare.PIXEL_STATES))
        expected='''\
     0 1 2 3 4 5 6 7 8 9 10 11 12 13
0    - - - - - - - - - - - - - -
1    - - - - - - - - - - - - - -
2    - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
3    - - ▣ - - - - - - - - ▣ - -
4    - - ▣ - - - - - - - - ▣ - -
5    - - ▣ - - - - - - - - ▣ - -
6    - - ▣ - - - - - - - - ▣ - -
7    - - ▣ - - - - - - - - ▣ - -
8    - - ▣ - - - - - - - - ▣ - -
9    - - ▣ - - - - - - - - ▣ - -
10   - - ▣ - - - - - - - - ▣ - -
11   - - ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ - -
12   - - - - - - - - - - - - - -
13   - - - - - - - - - - - - - -'''

        assert expected == result, f'expected {expected} != result {result}'
