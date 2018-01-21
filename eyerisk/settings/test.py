from .base import *
ALLOWED_HOSTS = ["*"]

# debug toolbar settings
try:
    DEBUG = (os.environ['DEBUG'] == "True")
except:
    DEBUG = False

DEBUG_TOOLBAR_PATCH_SETTINGS = False
if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# end debug toolbar settings
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
#DATABASES = {'default': dj_database_url.parse(url='postgres://eyerisk:waterzeug@localhost/eyerisk', conn_max_age=600)}
