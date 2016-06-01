import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import SelectionIndexView, SelectionCreateView


urlpatterns = [
    url(r'^$', SelectionIndexView.as_view(), name='index'),
    url(r'^selection/(?P<pk>\d+)$', SelectionIndexView.as_view(), name='selection-detail'),
    url(r'^selection/create$', SelectionCreateView.as_view(), name='selection-add'),
]
