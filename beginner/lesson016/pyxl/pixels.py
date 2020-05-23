from dataclasses import dataclass

@dataclass
class BinaryPixels:
    'The characters that represent each possible pixel state (full/empty)'

    full: str = '▣'
    empty: str = '▢'
