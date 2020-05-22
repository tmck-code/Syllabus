from dataclasses import dataclass
import math
from pyxl.grid import Pixels

def construct(*shape_classes):
    '''e.g.:
       C = shapes.construct(shapes.HollowSquare, shapes.DebugShape)
       C(5, 5)
    '''
    class ConstructedShape(*shape_classes): pass
    return ConstructedShape

# Superclasses ----------------------------------

@dataclass
class Shape:
    width:  int
    height: int
    pixels: Pixels = Pixels()

    def __post_init__(self): pass

    def fill_calculation(self, x, y) -> bool:
        raise NotImplementedError('Must implement fill_calculation(self, x, y) method')

    def should_fill(self, x, y):
        return bool(self.fill_calculation(x, y))

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
        '''This produces a number that is compared against the tolerance.
           If it is below (<) the required tolerance, the should_fill method
           will return True'''
        raise NotImplementedError('Must implement fill_calculation')


class DebugShape(FuzzyShape):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

    def pixel_to_draw(self, x, y):
        'If debug=True, then the pixel will be the value of fill_calculation'
        if self.debug:
            return str(self.fill_calculation(x, y))
        else:
            return self.pixels.full

class DebugCanvasShape(DebugShape):
    def should_fill(self, x, y):
        return True

    def pixel_to_draw(self, x, y):
        'If debug=True, then the pixel will be the value of fill_calculation'
        if self.debug:
            return str(int(self.fill_calculation(x, y)))
        else:
            return self.pixels.full

# Squares ---------------------------------------

class FilledSquare(Shape):
    def fill_calculation(self, x, y):
        return 0 <= x <= self.width and 0 <= y <= self.height


class HollowSquare(Shape):
    def fill_calculation(self, x, y):
        return 0 in (y % (self.width-1), x % (self.width-1))

# Circles ---------------------------------------

class FilledCircle(FuzzyShape):
    '''(x – h)2 + (y – k)2 = r2
       where (h,k) are the center coordinates, and r is the radius.'''

    def fill_calculation(self, x, y):
        h, k = int(self.width/2), int(self.height/2)
        r = int(self.width/2)
        return int((x-h)**2 + (y-k)**2) - r**2

class HollowCircle(FilledCircle):
    def should_fill(self, x, y):
        return -self.tolerance <= self.fill_calculation(x, y) < self.tolerance

# Curves ----------------------------------------

class Exponential(FuzzyShape):
    def fill_calculation(self, x, y):
        return abs((x**2) - y)