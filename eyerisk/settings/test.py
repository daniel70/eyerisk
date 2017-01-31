from .base import *
from .secrets import *
ALLOWED_HOSTS = ["*"]

# debug toolbar settings
DEBUG = True

DEBUG_TOOLBAR_PATCH_SETTINGS = False
INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE_CLASSES.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# end debug toolbar settings

DATABASES = {'default': dj_database_url.parse(url='postgres://eyerisk:waterzeug@localhost/eyerisk', conn_max_age=600)}
