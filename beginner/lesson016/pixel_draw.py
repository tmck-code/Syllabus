#!/usr/bin/env python3

import sys
from argparse import ArgumentParser

import grid
from shapes import *

def run(shape, width=10, height=10, padding=2, full='▣', empty='▢'):
    try:
        # hack - search through all modules imported from shapes using globals()
        g = grid.CartesianGrid(
            width        = width,
            height       = height,
            padding      = padding,
            pixel_states = grid.PixelStates(full, empty)
        )
        obj = globals()[shape](width=width, height=height)
        g.draw(obj)
        print(f'{width}x{height} {shape}')
        print(g)
    except Exception as e:
        raise e
        print(f'{e.__class__.__name__}: {e}')
        sys.exit(1)

if __name__ == '__main__':
    parser = ArgumentParser(description='Takes in a file of client data, cleans and inserts into a DB')
    # import configuration arguments
    parser.add_argument('-s', '--shape',   action='store', help='shape to draw',                 type=str, required=True, dest='shape')
    parser.add_argument('-w', '--width',   action='store', help='width in pixels, default: 10',  type=int, default=10,    dest='width')
    parser.add_argument('-H', '--height',  action='store', help='height in pixels, default: 10', type=int, default=10,    dest='height')
    parser.add_argument('-p', '--padding', action='store', help='padding in pixels, default: 2', type=int, default=2,     dest='padding')
    parser.add_argument('-e', '--empty',   action='store', help='empty pixel, default: ▣',       type=str, default='▢',   dest='empty')
    parser.add_argument('-f', '--full',    action='store', help='full pixel, default: ▢',        type=str, default='▣',   dest='full')
    run(**parser.parse_args().__dict__)
