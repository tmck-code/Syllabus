import shapes

class Pattern:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def seq(self):
        raise NotImplementedError

class Ring(Pattern):
    @property
    def seq(self):
        yield from [
            (shapes.HollowCircle(self.width, self.height, tolerance=int(self.width/2)), {'dx': 0, 'dy': 0}),
            (shapes.HollowCircle(self.width-6, self.height-6, tolerance=int(self.width/2)), {'dx': 0, 'dy': 0}),
        ]

# e.g.
# g = grid.CartesianGrid(41, 41, pixels=grid.Pixels(empty=' '))
# draw_on_grid(g, patterns.Ring(21, 21))
def draw_on_grid(grid, pattern):
    for s, kwargs in pattern.seq:
        grid.draw(s, **kwargs)
