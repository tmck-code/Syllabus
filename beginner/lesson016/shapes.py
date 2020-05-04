import math
from grid import PixelStates

class Shape:

    def __init__(self, width, height, pixel_states: PixelStates = PixelStates()):
        self.width = width
        self.height = height
        self.pixel_states = pixel_states
        self.__post_init__()

    def __post_init__(self):
        pass

    def should_fill(self, x, y):
        raise NotImplementedError('Must implement should_fill(self, x, y) method')

    def draw(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.should_fill(x, y):
                    yield x, y, self.pixel_states.full

    def __str__(self):
        return f'{self.__class__.__name__}, coords: ' + list(self.draw())

# Squares ---------------------------------------

class FilledSquare(Shape):

    def should_fill(self, x, y):
        return 0 <= x <= self.width and 0 <= y <= self.height


class HollowSquare(Shape):

    def should_fill(self, x, y):
        return 0 in (y % (self.width-1), x % (self.width-1))

# Circles ---------------------------------------

class FilledCircle(Shape):
    '''
    from: https://www.purplemath.com/modules/sqrcircle.htm

    The technique of completing the square is used to turn a quadratic into the
    sum of a squared binomial and a number: (x – a)2 + b.
    The center-radius form of the circle equation is in the format

        (x – h)2 + (y – k)2 = r2

    where
        (h,k) are the center coordinates, and
        r is the radius.

    This form of the equation is helpful, since you can easily find the center and the radius.
    '''

    def __post_init__(self):
        if not is_odd(self.width):
            raise AttributeError('Must create circles with odd-numbered width & height')

    def should_fill(self, x, y, tolerance=3):
        h, k = int(self.width/2), int(self.height/2)
        l = int((x-h)**2 + (y-k)**2)
        r = int(self.width/2)**2

        return l - r <= tolerance


def is_odd(n):
    return n & 1

