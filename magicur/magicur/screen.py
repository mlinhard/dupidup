'''
Created on 12 Sep 2019

@author: mlinhard
'''
from magicur.palette import Palette


class MagicWindow(object):

    def __init__(self, parent, window, log, app):
        self._parent = parent
        self._window = window
        self._log = log
        self._app = app

    def put_text(self, x, y, text):
        try:
            self._window.addstr(y, x, text)
        except:
            self._log.debug("addstr thrown")

    def set_paint(self, x, y, length, color_pair_key):
        self._window.chgat(y, x, length, self._app._palette.color_pair(color_pair_key))

    def reset_to(self, char, color_pair_key):
        self._window.bkgd(char, Palette.instance().color_pair(color_pair_key))
        self._window.erase()

    def sub_window(self, width, height, x, y):
        return MagicWindow(self, self._window.subwin(height, width, y, x), self._log, self._app)

    def refresh(self):
        self._window.refresh()

    def size(self):
        height, width = self._window.getmaxyx()
        return width, height

    @property
    def width(self):
        return self.size()[0]

    @property
    def height(self):
        return self.size()[1]


class MagicScreen(object):

    def __init__(self, stdscr, log, app):
        self._stdscr = stdscr
        self._log = log
        self._app = app
        self._children = []

    def clear(self):
        self._win.reset_to(" ", "black lightgray")

    def getch(self):
        return self._stdscr.getch()

    def ungetch(self, ch):
        return self._stdscr.ungetch(ch)

    def size(self):
        height, width = self._stdscr.getmaxyx()
        return width, height

    @property
    def width(self):
        return self.size()[0]

    @property
    def height(self):
        return self.size()[1]

    def palette(self):
        return Palette.instance()

    def sub_window(self, width, height, x, y):
        return MagicWindow(self, self._stdscr.subwin(height, width, y, x), self._log, self._app)

    def pad(self, width, height, x, y):
        return MagicWindow(self, self._stdscr.newpad(height, width, y, x), self._log, self._app)
