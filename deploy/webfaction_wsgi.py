import sys, os

# handle the virtualenv
activate_this = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'env/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from calebcc import app
application = app
