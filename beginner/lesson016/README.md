# The pixel grid

Welcome to the pixel grid!

## CLI

You can draw a single shape on a grid from the command-line.

e.g. To draw an 11x11 filled square, with a padding of 2 and custom pixels

```shell
 ☯ ~/P/d/S/b/lesson016 ./draw.py -s FilledSquare -w 11 -H 11 -e ' ' -f 'X'
11x11 FilledSquare
     0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
0
1
2        X X X X X X X X X X X
3        X X X X X X X X X X X
4        X X X X X X X X X X X
5        X X X X X X X X X X X
6        X X X X X X X X X X X
7        X X X X X X X X X X X
8        X X X X X X X X X X X
9        X X X X X X X X X X X
10       X X X X X X X X X X X
11       X X X X X X X X X X X
12       X X X X X X X X X X X
13
14
```

## IPython

> Hint: `python3 -m pip install ipython`


```
import grid
from shapes import *

# Set up the grid
g = grid.CartesianGrid(31, 31, 2, pixel_states=PixelStates(empty=' '))

# Set up 2 shapes and draw them on the grid
s1 = HollowSquare(13, 13, pixel_states=grid.PixelStates(full='X'))
s2 = FilledCircle(17, 17)

g.draw(s1, s2)

# Now render the grid!
print(g)
```
