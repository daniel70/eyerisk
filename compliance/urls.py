import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import SelectionIndexView


urlpatterns = [
    url(r'^$', SelectionIndexView.as_view(), name='index'),
]