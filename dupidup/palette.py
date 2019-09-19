#!/usr/bin/python3
"""Magic curses palette

Usage:
  magicur [options]

Options:
  -h --help   Show this screen.
  --version   Show version.
  --debug-log <log-file> Debug logging to file exactly.log in current directory
  --debug <debug-string> Start PyDev debug server. Debug string format: host:port:pydev_src
"""
import sys

from docopt import docopt
from magicur.app import MagicApplication, MagicBootstrap


class PaletteApplication(MagicApplication):
    
    def init_palette(self, palette):
        palette.add_color("0", "282a2e")
        palette.add_color("1", "a54242")
        palette.add_color("2", "8c9440")
        palette.add_color("3", "de935f")
        palette.add_color("4", "5f819d")
        palette.add_color("5", "85678f")
        palette.add_color("6", "5e8d87")
        palette.add_color("7", "707880")
        palette.add_color("8", "373b41")
        palette.add_color("9", "cc6666")
        palette.add_color("10", "b5bd68")
        palette.add_color("11", "f0c674")
        palette.add_color("12", "81a2be")
        palette.add_color("13", "b294bb")
        palette.add_color("14", "8abeb7")
        palette.add_color("15", "c5c8c6")
        palette.add_color("BG", "1d1f21")
        palette.add_color("FG", "c5c8c6")

        for i in range(16):
            palette.add_pair("FG_" + str(i), "FG", str(i))

        for i in range(16):
            palette.add_pair("BG_" + str(i), "BG", str(i))

    def init_view(self, screen):
        win = screen.sub_window(screen.width, screen.height, 0, 0)
        win.reset_to(" ", "default")

        for i in range(16):
            win.put_text(2, i + 1, str(i).rjust(2, " "))
            bar = win.sub_window(8, 1, 10, i + 1)
            bar.reset_to(" ", "FG_" + str(i))
            bar.put_text(0, 0, "FG " + str(i).rjust(2, " "))

            bar = win.sub_window(8, 1, 20, i + 1)
            bar.reset_to(" ", "BG_" + str(i))
            bar.put_text(0, 0, "BG " + str(i).rjust(2, " "))
        win.refresh()


if __name__ == '__main__':
    args = docopt(__doc__, version="0.1.0")
    temp_datadir = "session"
    if "--temp-datadir" in args and args["--temp-datadir"] != None:
        temp_datadir = args["--temp-datadir"]
    
    application = PaletteApplication()
    magic = MagicBootstrap(debug_log_file=args['--debug-log'], debug_string=args['--debug'])
    sys.exit(magic.run(application))
