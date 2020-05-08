import math
from grid import Pixels

def construct(*shape_classes):
    '''example usage:
       C = shapes.construct(shapes.HollowSquare, shapes.DebugShape)
       C(5, 5)
    '''
    class ConstructedShape(*shape_classes): pass
    return ConstructedShape

# Superclasses ----------------------------------

class Shape:

    def __init__(self, width, height, pixels: Pixels = Pixels()):
        self.width = width
        self.height = height
        self.pixels = pixels
        self.__post_init__()

    def __post_init__(self):
        pass

    def should_fill(self, x, y):
        raise NotImplementedError('Must implement should_fill(self, x, y) method')

    def pixel_to_draw(self, x, y):
        return self.pixels.full

    def draw(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.should_fill(x, y):
                    yield x, y, self.pixel_to_draw(x, y)

    def __str__(self):
        return f'{self.__class__.__name__}, coords: ' + list(self.draw())


class FuzzyShape(Shape):

    def __init__(self, *args, tolerance=2, **kwargs):
        super().__init__(*args, **kwargs)
        self.tolerance = tolerance

    def should_fill(self, x, y):
        return self.fill_calculation(x, y) < self.tolerance

    def fill_calculation(self, x, y):
        raise NotImplementedError('Must implement fill_calculation')


class DebugShape(FuzzyShape):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

    def fill_calculation(self, x, y):
        return int(self.should_fill(x, y))

    def pixel_to_draw(self, x, y):
        if self.debug:
            return str(self.fill_calculation(x, y))
        else:
            return self.pixels.full

# Squares ---------------------------------------

class FilledSquare(Shape):
    def should_fill(self, x, y):
        return 0 <= x <= self.width and 0 <= y <= self.height


class HollowSquare(Shape):
    def should_fill(self, x, y):
        return 0 in (y % (self.width-1), x % (self.width-1))

# Circles ---------------------------------------

class FilledCircle(FuzzyShape):
    '''(x – h)2 + (y – k)2 = r2
       where (h,k) are the center coordinates, and r is the radius.'''

    def fill_calculation(self, x, y):
        h, k = int(self.width/2), int(self.height/2)
        r = int(self.width/2)
        return int((x-h)**2 + (y-k)**2) - r**2

# Curves ----------------------------------------

class Exponential(FuzzyShape):
    def fill_calculation(self, x, y):
        return abs((x**2) - y)

