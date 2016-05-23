import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import index

urlpatterns = [
    url(r'^$', index, name='index'),
    url('^', include('django.contrib.auth.urls')),
]