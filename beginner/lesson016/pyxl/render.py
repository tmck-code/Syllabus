from dataclasses import dataclass

@dataclass
class Renderer:
    '''An x-y pixel renderer.'''
    width: int
    height: int

@dataclass
class CartesianGrid(Renderer):
    '''An x-y pixel grid. Optionally set padding width, and empty pixel'''
    DEFAULT_EMPTY_PIXEL = '▢'

    padding: int = 0
    empty_pixel: str = DEFAULT_EMPTY_PIXEL

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

    def clear(self):
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


@dataclass
class FillCommands(Renderer):
    pass
    def draw(self, *shapes):
        for s in shapes:
            for x, y, p in s.draw():
                yield f'/fill {x} {y} 64 {x} {y} 64 {p}'

