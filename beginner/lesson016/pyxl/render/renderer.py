from dataclasses import dataclass

@dataclass
class Renderer:
    '''An x-y pixel renderer.'''

    width: int
    height: int

    def __post_init__(self):
        pass
