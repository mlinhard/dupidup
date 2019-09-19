#!/usr/bin/python3
"""Dupi-Dup File deduplication tool 

Usage:
  dupidup [options] [<folder>...] (--ignore <ignored-dir>)...

Options:
  -h, --help                     Show this screen.
  --version                      Show version.
  --temp-datadir <temp-datadir>  Use given temp datadir file.
  --ignore <ignored-dir>         Ignore directory and it's subtree
  --debug-level          Set DEBUG level for server log
  --debug-log <log-file> Debug logging to file exactly.log in current directory
  --debug <debug-string> Start PyDev debug server. Debug string format: host:port:pydev_src  
"""
import sys

from magicur.app import MagicBootstrap

from docopt import docopt
from dupidup.app import DupidupApplication

VERSION = '0.1.0'

if __name__ == '__main__':
    args = docopt(__doc__, version=VERSION)
    temp_datadir = "session"
    if "--temp-datadir" in args and args["--temp-datadir"] != None:
        temp_datadir = args["--temp-datadir"]

    application = DupidupApplication(temp_datadir, args["<folder>"], args["--ignore"])
    magic = MagicBootstrap(debug_log_file=args['--debug-log'], debug_string=args['--debug'])
    sys.exit(magic.run(application))

