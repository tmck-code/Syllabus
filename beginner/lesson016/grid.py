from dataclasses import dataclass
from enum import Enum

@dataclass
class PixelStates:
    'Holds the two characters representing possible pixel state (full/empty)'

    full:  str = '▣'
    empty: str = '▢'


class CartesianGrid:

    def __init__(self, width: int, height: int, padding: int = 0, pixel_states: PixelStates = PixelStates()):
        self.width = width
        self.height = height
        self.padding = padding
        self.pixel_states = pixel_states
        self.grid = self.create_grid()

    def create_grid(self):
        self.grid = []
        self.clear_grid()

    def clear_grid(self):
        self.grid = []
        for _ in range(0, self.height+(self.padding*2)):
            self.grid.append([self.pixel_states.empty for _ in range(0, self.width+(self.padding*2))])

    def draw(self, *shapes, dx=0, dy=0, render=False):
        # Calculate the x, y of the grid center
        h, k = int(self.width/2), int(self.height/2)
        for shape in shapes:
            # Calculate the x, y of the top-left corner of the shape so that it is
            # positioned in the centre of the grid
            cx, cy = h-int(shape.width/2)+dx, k-int(shape.height/2)+dy
            for p, q, pixel in shape.draw():
                self.fill_cell(p+cx, q+cy, pixel)
        if render:
            print(self.__str__())

    def fill_cell(self, x, y, pixel_state):
        self.grid[y+self.padding][x+self.padding] = pixel_state

    def __str__(self):
        result = [' '*5 + ' '.join(map(str, range(0, len(self.grid[0]))))]
        for i, row in enumerate(self.grid):
            result.append(' '.join(['{:<4d}'.format(i)] + row))
        return '\n'.join(result)

