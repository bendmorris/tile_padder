#!/usr/bin/env python
# usage: python tile_padder.py (tileset) (tile size) (old padding) (new padding)
import sys
import pygame

ALPHA = 0

input_file = sys.argv[1]
tile_size = int(sys.argv[2])
old_padding = int(sys.argv[3]) if len(sys.argv) > 3 else 0
new_padding = int(sys.argv[4]) if len(sys.argv) > 4 else 1

old_tile = tile_size + old_padding * 2
new_tile = tile_size + new_padding * 2

image = pygame.image.load(input_file)

width, height = image.get_size()

surf = pygame.Surface((width / old_tile * new_tile, height / old_tile * new_tile), pygame.SRCALPHA)
surf.set_alpha(True)

# fill in tile pixels
for x in range(width / old_tile):
    for y in range(height / old_tile):
        for xi in range(tile_size):
            for yi in range(tile_size):
                color = image.get_at((x*old_tile + old_padding + xi, y*old_tile + old_padding + yi))
                surf.set_at((x*new_tile + new_padding + xi, y*new_tile + new_padding + yi), color)

def average_color(colors):
    r = 0
    g = 0
    b = 0
    for (ri, gi, bi, _) in colors:
        r += ri
        g += gi
        b += bi
    return (int(round(r/len(colors))), int(round(g/len(colors))), int(round(b/len(colors))), ALPHA)

# fill in transparent pixels with average of surrounding values to avoid bleed
for x in range(width / old_tile):
    for y in range(height / old_tile):
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

        for xi in range(tile_size):
            for yi in range(tile_size):
                c = surf.get_at((x*new_tile + new_padding + xi, y*new_tile + new_padding + yi))
                if c.a == 0:
                    surf.set_at((x*new_tile + new_padding + xi, y*new_tile + new_padding + yi), get_value(xi, yi))

        # fill spacing with transparent color values to avoid black bleed
        for i in range(new_tile):
            # top left corner
            if i == 0:
                color = surf.get_at((x*new_tile + new_padding, y*new_tile + new_padding))
                color.a = ALPHA
                for xi in range(new_padding):
                    for yi in range(new_padding):
                        surf.set_at((x*new_tile + xi, y*new_tile + yi), color)
                continue
            elif i < new_padding: continue

            for bi in range(new_padding):
                # top padding
                color = surf.get_at((x*new_tile + i, y*new_tile + new_padding))
                color.a = ALPHA
                surf.set_at((x*new_tile + i, y*new_tile + bi), color)
                # bottom padding
                color = surf.get_at((x*new_tile + i, y*new_tile + new_padding + tile_size - 1))
                color.a = ALPHA
                surf.set_at((x*new_tile + i, y*new_tile + new_padding + tile_size + bi), color)
                # left padding
                color = surf.get_at((x*new_tile + new_padding, y*new_tile + i))
                color.a = ALPHA
                surf.set_at((x*new_tile + bi, y*new_tile + i), color)
                # right padding
                color = surf.get_at((x*new_tile + new_padding + tile_size - 1, y*new_tile + i))
                color.a = ALPHA
                surf.set_at((x*new_tile + new_padding + tile_size + bi, y*new_tile + i), color)

pygame.image.save(surf, 'output.png')