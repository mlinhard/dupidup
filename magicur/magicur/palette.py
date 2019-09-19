'''
Magic Palette
'''
from curses import color_pair, init_pair, init_color
import curses


class Palette(object):

    _singleton = None

    @classmethod
    def instance(cls):
        if cls._singleton == None:
            cls._singleton = Palette()
        return cls._singleton

    def __init__(self):
        if Palette._singleton != None:
            raise Exception("Palette is signleton!")
        self.reset()

    def add_default_colors(self):
        self.add_color("black", "282a2e")
        self.add_color("red", "a54242")
        self.add_color("green", "8c9440")
        self.add_color("orange", "de935f")
        self.add_color("blue", "5f819d")
        self.add_color("purple", "85678f")
        self.add_color("cyan", "5e8d87")
        self.add_color("gray", "707880")
        self.add_color("lightblack", "373b41")
        self.add_color("lightred", "cc6666")
        self.add_color("lightgreen", "b5bd68")
        self.add_color("yellow", "f0c674")
        self.add_color("lightblue", "81a2be")
        self.add_color("lightpurple", "b294bb")
        self.add_color("lightcyan", "8abeb7")
        self.add_color("lightgray", "c5c8c6")
        self.add_color("white", "ffffff")

        self.add_color("BG", "1d1f21")
        self.add_color("FG", "c5c8c6")

    def reset(self):
        self._colors_by_key = {}
        self._pairs_by_key = {"default":0}

    def add_color(self, key, hexcolor):
        if len(self._colors_by_key) >= curses.COLORS:
            raise Exception("Maximum number of colors reached")
        r1, g1, b1 = Palette._rgb_from_hex(hexcolor)
        r2, g2, b2 = Palette._rgb1000(r1, g1, b1)

        color_idx = self._colors_by_key.get(key)
        if color_idx == None:
            color_idx = len(self._colors_by_key)
            self._colors_by_key[key] = color_idx

        init_color(color_idx, r2, g2, b2)

    def add_pair(self, pair_key, fg_key, bg_key):
        if len(self._pairs_by_key) >= curses.COLORS:
            raise Exception("Maximum number of color pairs reached")
        fg = self._colors_by_key[fg_key]
        bg = self._colors_by_key[bg_key]
        pair_idx = self._pairs_by_key.get(pair_key)
        if pair_idx == None:
            pair_idx = len(self._pairs_by_key)
            self._pairs_by_key[pair_key] = pair_idx
        init_pair(pair_idx, fg, bg)

    def color_pair(self, pair_key):
        return color_pair(self._pairs_by_key[pair_key])

    @staticmethod
    def _rgb1000(r, g, b):
        return round(1000 * (r / 256)), round(1000 * (g / 256)), round(1000 * (b / 256))

    @staticmethod
    def _rgb_from_hex(hexcolor):
        if hexcolor.startswith("#"):
            hexcolor = hexcolor[1:]
        if len(hexcolor) != 6:
            raise Exception(f"Wrong color definition: {hexcolor}")
        return int(hexcolor[0:2], 16), int(hexcolor[2:4], 16), int(hexcolor[4:6], 16)

