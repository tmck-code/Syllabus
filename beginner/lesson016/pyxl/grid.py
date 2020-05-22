from dataclasses import dataclass

@dataclass
class Pixels:
    'The characters that represent each possible pixel state (full/empty)'

    full: str = '▣'
    empty: str = '▢'


@dataclass
class CartesianGrid:
    '''An x-y pixel grid. Optionally set padding width, and empty pixel'''

    width: int
    height: int
    padding: int = 0
    empty_pixel: str = Pixels.empty

    def __post_init__(self):
        self.grid = self.__create_grid()

    def draw(self, *shapes, dx=0, dy=0):
        '''Draw shapes on the canvas, with the shapes' starting coordinate optionally
        offset by (dx, dy).'''

        # Calculate (x, y) for the grid center
        h, k = int(self.width/2), int(self.height/2)
        for shape in shapes:
            # Calculate (x, y) for the top-left corner of the shape, so that it is positioned in the
            # centre of the grid
            cx, cy = h-int(shape.width/2)+dx, k-int(shape.height/2)+dy
            for p, q, pixel in shape.draw():
                self.__fill_cell(x=p+cx, y=q+cy, pixel=pixel)

    def clear_grid(self):
        'Set the grid to its initial state, removing any drawn shapes'
        self.grid = self.__create_grid()

    def __create_grid(self):
        grid = []
        for _ in range(0, self.height+(self.padding*2)):
            grid.append([self.empty_pixel for _ in range(0, self.width+(self.padding*2))])
        return grid

    def __fill_cell(self, x, y, pixel):
        self.grid[y+self.padding][x+self.padding] = pixel

    def __str__(self):
        result = [' '*5 + ' '.join(map(str, range(0, len(self.grid[0]))))]
        for i, row in enumerate(self.grid):
            result.append(' '.join(['{:<4d}'.format(i)] + row))
        return '\n'.join(result)

