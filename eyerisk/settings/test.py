from .base import *
from .secrets import *

DEBUG = True

INSTALLED_APPS += [
    'debug_toolbar',
]
DATABASES = {'default': dj_database_url.parse(url='postgres://eyerisk:waterzeug@localhost/eyerisk', conn_max_age=600)}