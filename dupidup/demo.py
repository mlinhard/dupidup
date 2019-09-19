#!/usr/bin/python3
"""Magic curses demo 

Usage:
  magicur [options]

Options:
  -h --help   Show this screen.
  --version   Show version.
  --debug-log <log-file> Debug logging to file exactly.log in current directory
  --debug <debug-string> Start PyDev debug server. Debug string format: host:port:pydev_src
"""
from docopt import docopt
import sys
from dupidup.demoapp import DemoApplication
from magicur.app import MagicBootstrap

if __name__ == '__main__':
    args = docopt(__doc__, version="0.1.0")
    magic = MagicBootstrap(debug_log_file=args['--debug-log'], debug_string=args['--debug'])
    sys.exit(magic.run(DemoApplication()))