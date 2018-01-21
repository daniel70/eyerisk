from .base import *

try:
    DEBUG = (os.environ['DEBUG'] == "True")
except:
    DEBUG = False


ALLOWED_HOSTS = [".herokuapp.com", "www.eyerisk.nl" ]
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
