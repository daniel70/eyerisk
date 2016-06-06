import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import SelectionDetailView, SelectionListView, SelectionCreateView


urlpatterns = [
    url(r'^selection/$', SelectionListView.as_view(), name='selection-list'),
    url(r'^selection/(?P<pk>\d+)/$', SelectionDetailView.as_view(), name='selection-detail'),
    url(r'^selection/create$', SelectionCreateView.as_view(), name='selection-add'),
]
