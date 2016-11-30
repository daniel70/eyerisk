from .base import *

DEBUG = False
ALLOWED_HOSTS = [".herokuapp.com", "0.0.0.0" ]
MIDDLEWARE_CLASSES.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
