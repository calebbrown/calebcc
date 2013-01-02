import os
import sys

if 'CALEBCC_CONFIG_MODULE' not in os.environ:
    os.environ['CALEBCC_CONFIG_MODULE'] = 'env.dev'

from bottle import run, debug

from main import app, parser

def main(argv):
    if '--parse' in argv:
        argv.pop(argv.index('--parse'))

        print "Parsing docs..."
        parser.run()
    else:
        debug(True)
        run(app, host='localhost', port=8080, reloader=True)

if __name__ == '__main__':
    main(sys.argv)

