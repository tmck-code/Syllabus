from collections import namedtuple
from dataclasses import dataclass

Config = namedtuple('Config', ['a', 'b'])


@dataclass
class Obj:
    a: int = 1
    b: int = 2
    c: str = 'default'


Obj(1).a + 's'
def test_nt():
    Config(1,2).a + 'a'