'''
Created on 18 Sep 2019

@author: mlinhard
'''
from magicur.screen import MagicWindow


class TestMagicWindow(MagicWindow):

    def __init__(self, width, height, x, y):
        self._x, self._y = x, y
        self._width, self._height = width, height
        self.line = None
        self.reset_to(" ", None)
        self.children = []

    def put_text(self, x, y, text):
        if x >= self._width:
            raise Exception(f"Can't put text at x={x}, width={self._width}")
        if y >= self._height:
            raise Exception(f"Can't put text at y={y}, height={self._height}")
        old = self.line[y]
        new = old[:x] + text[:self._width - x] + old[x + len(text):self._width]
        self.line[y] = new
        if len(text) + x > self._width and y + 1 < self._height:
            self.put_text(0, y + 1, text[self._width - x:])

    def set_paint(self, x, y, length, color_pair_key):
        pass

    def reset_to(self, char, color_pair_key):
        self.line = [char * self._width for _ in range(self._height)]

    def sub_window(self, width, height, x, y):
        child = TestMagicWindow(width, height, x, y)
        self.children.append(child)
        return child

    def refresh(self):
        pass

    def size(self):
        return self._width, self._height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def contents(self):
        return "\n".join(self.line) + "\n"

