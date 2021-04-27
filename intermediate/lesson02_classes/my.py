from collections import namedtuple

Config = namedtuple('Config', ['a', 'b'])

def test_nt():
    Config(1,2).a + 'a'

from dataclasses import dataclass

@dataclass
class Obj:
    a: int = 1
    b: int = 2
    c: str = 'default'

def test_dc():
    Obj(1).a + 's'