#!/usr/bin/env python
import sys
import pygame
import math

def run(args):
    input_file = args.input_file
    output_file = args.output or input_file
    tile_size = args.tile_size
    old_padding = args.old_padding
    new_padding = args.padding

    old_tile = tile_size + old_padding * 2
    new_tile = tile_size + new_padding * 2

    image = pygame.image.load(input_file)

    width, height = image.get_size()

    dx = width / old_tile * new_tile
    dy = height / old_tile * new_tile
    if args.pot:
        dx = int(2 ** math.ceil(math.log(dx, 2)))
        dy = int(2 ** math.ceil(math.log(dy, 2)))
    if args.square:
        dx = max(dx, dy)
        dy = dx

    surf = pygame.Surface((dx, dy), pygame.SRCALPHA)
    surf.set_alpha(True)

    # fill in tile pixels
    for x in range(width // old_tile):
        for y in range(height // old_tile):
            for xi in range(tile_size):
                for yi in range(tile_size):
                    color = image.get_at((x*old_tile + old_padding + xi, y*old_tile + old_padding + yi))
                    surf.set_at((x*new_tile + new_padding + xi, y*new_tile + new_padding + yi), color)

    if args.bleed:
        def average_color(colors):
            r = 0
            g = 0
            b = 0
            a = 0
            for (ri, gi, bi, ai) in colors:
                r += ri
                g += gi
                b += bi
                a += ai
            return (int(round(r/len(colors))), int(round(g/len(colors))), int(round(b/len(colors))), int(round(a/len(colors))))

        # fill in transparent pixels with average of surrounding values to avoid bleed
        for x in range(width // old_tile):
            for y in range(height // old_tile):
                cs = []
                for xi in range(tile_size):
                    for yi in range(tile_size):
                        c = surf.get_at((x*new_tile + new_padding + xi, y*new_tile + new_padding + yi))
                        if c.a > 0:
                            cs.append((xi, yi, c))

                if len(cs) == 0: continue

                def get_value(xi, yi):
                    min_d = min([abs(xi-xii) + abs(yi-yii) for (xii, yii, c) in cs])
                    colors = [c for (xii, yii, c) in cs if abs(xi-xii) + abs(yi-yii) == min_d]
                    return average_color(colors)

                # fill spacing with transparent color values to avoid black bleed
                for i in range(new_tile):
                    # top left corner
                    if i == 0:
                        color = surf.get_at((x*new_tile + new_padding, y*new_tile + new_padding))
                        for xi in range(new_padding):
                            for yi in range(new_padding):
                                surf.set_at((x*new_tile + xi, y*new_tile + yi), color)
                        continue
                    elif i < new_padding: continue

                    for bi in range(new_padding):
                        # top padding
                        color = surf.get_at((x*new_tile + i, y*new_tile + new_padding))
                        surf.set_at((x*new_tile + i, y*new_tile + bi), color)
                        # bottom padding
                        color = surf.get_at((x*new_tile + i, y*new_tile + new_padding + tile_size - 1))
                        surf.set_at((x*new_tile + i, y*new_tile + new_padding + tile_size + bi), color)
                        # left padding
                        color = surf.get_at((x*new_tile + new_padding, y*new_tile + i))
                        surf.set_at((x*new_tile + bi, y*new_tile + i), color)
                        # right padding
                        color = surf.get_at((x*new_tile + new_padding + tile_size - 1, y*new_tile + i))
                        surf.set_at((x*new_tile + new_padding + tile_size + bi, y*new_tile + i), color)

    pygame.image.save(surf, output_file)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='tile_padder')
    parser.add_argument('input_file', help='path to font file; output files will be saved in this directory')
    parser.add_argument('--tile_size', '-t', type=int, help='tile dimensions (square)')
    parser.add_argument('--output', '-o', nargs='?', default=None,
                        help='output file path (extension ignored, none to modify in place)')
    parser.add_argument('--pot', action='store_true', help='make the dimensions of the resulting output file a power of two')
    parser.add_argument('--square', action='store_true', help='make the dimensions of the resulting output file equal')
    parser.add_argument('--bleed', action='store_true', help='add bleed correction')
    parser.add_argument('--padding', '-p', type=int, default=1, help='amount to pad each side of the tiles')
    parser.add_argument('--old-padding', type=int, default=0, help='if provided, amount of padding this tileset already contains')

    args = parser.parse_args()

    run(args)

if __name__ == '__main__':
    main()
