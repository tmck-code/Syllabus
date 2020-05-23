from dataclasses import dataclass

from pyxl.render.renderer import Renderer

@dataclass
class FillCommands(Renderer):
    pass
    def draw(self, *shapes):
        for s in shapes:
            for x, y, p in s.draw():
                yield f'/fill {x} {y} 64 {x} {y} 64 {p}'

