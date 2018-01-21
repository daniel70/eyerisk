from .base import *
ALLOWED_HOSTS = ["0.0.0.0", ".herokuapp.com", "www.eyerisk.nl" ]

try:
    DEBUG = (os.environ['DEBUG'] == "True")
except:
    DEBUG = False

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
