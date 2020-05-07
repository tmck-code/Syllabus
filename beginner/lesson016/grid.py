from dataclasses import dataclass
from enum import Enum

@dataclass
class Pixels:
    'Holds the two characters representing possible pixel state (full/empty)'

    full:  str = '▣'
    empty: str = '▢'


class CartesianGrid:
    '''An x-y pixel grid. Optionally set padding width, and empty pixel that is used for all cells
    in the 'blank' canvas'''

    def __init__(self, width: int, height: int, padding=0, pixels=Pixels()):
        self.width = width
        self.height = height
        self.padding = padding
        self.pixels = pixels
        self.grid = self.__create_grid()

    def draw(self, *shapes, dx=0, dy=0, render=False):
        '''Draws 1+ shapes on the canvas, with the shapes' starting coordinate optionally
        translated by dx & dy. If render is True, returns the grid as a string'''

        # Calculate the x, y of the grid center
        h, k = int(self.width/2), int(self.height/2)
        for shape in shapes:
            # Calculate the x, y of the top-left corner of the shape so that it is
            # positioned in the centre of the grid
            cx, cy = h-int(shape.width/2)+dx, k-int(shape.height/2)+dy
            for p, q, pixel in shape.draw():
                self.__fill_cell(x=p+cx, y=q+cy, pixel=pixel)
        if render:
            return self.__str__()

    def clear_grid(self):
        'Sets the grid to its initial state, removing any drawn shapes'
        self.grid = self.__create_grid()

    def __create_grid(self):
        grid = []
        for _ in range(0, self.height+(self.padding*2)):
            grid.append([self.pixels.empty for _ in range(0, self.width+(self.padding*2))])
        return grid

    def __fill_cell(self, x, y, pixel):
        self.grid[y+self.padding][x+self.padding] = pixel

    def __str__(self):
        result = [' '*5 + ' '.join(map(str, range(0, len(self.grid[0]))))]
        for i, row in enumerate(self.grid):
            result.append(' '.join(['{:<4d}'.format(i)] + row))
        return '\n'.join(result)

