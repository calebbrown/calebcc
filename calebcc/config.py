import os
import sys
import importlib

# import ourselves so we can set overrides from a local module
import config

# Setup paths
LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_SOURCE = os.path.abspath(os.path.join(PROJECT_PATH, '../site_data'))
DATA_STORE = os.path.abspath(os.path.join(PROJECT_PATH, '../compiled_data'))
TEMPLATE_PATHS = [
    os.path.join(LOCAL_PATH, 'views'),
]

DEFAULT_FORMAT = 'markdown'

SITE_NAME = 'calebbrown.id.au'
SITE_BASE = 'http://calebbrown.id.au/'

CHANNEL_OPTIONS = (
    ('meta', 'Meta'),
    ('life', 'Life'),
    ('tech', 'Tech'),
    ('legacy', 'Legacy'),
)

# The time in days before we start showing adverts of blog posts
ADVERT_LIMIT = 40

MEMCACHE_SOCK = 'unix:' + os.path.expanduser('~/memcached.sock')


# load up local environment configuration
if 'CALEBCC_CONFIG_MODULE' in os.environ:
    config_mod_name = os.environ['CALEBCC_CONFIG_MODULE']
    mod = importlib.import_module(config_mod_name)
    for (k,v) in mod.__dict__.iteritems():
        if k[0] == '_': # skip anything starting with an underscore
            continue
        if k in sys.modules: # skip anything that is a module
            continue
        setattr(config, k, v)

# setup the cache
# TODO: move this into it's own module
try:
    import memcache
    CACHE = memcache.Client([MEMCACHE_SOCK], debug=0)
except:
    class DummyCache(object):
        def get(self, *args, **kwargs):
            return None
        def set(self, *args, **kwargs):
            pass
    CACHE = DummyCache()

