import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import SelectionDetail, SelectionList, SelectionCreate, SelectionUpdate, SelectionDelete


urlpatterns = [
    url(r'^$', SelectionList.as_view(), name='risk-home'),
    url(r'^selection/$', SelectionList.as_view(), name='selection-list'),
    url(r'^selection/(?P<pk>\d+)/$', SelectionDetail.as_view(), name='selection-detail'),
    url(r'^selection/create$', SelectionCreate.as_view(), name='selection-add'),
    url(r'^selection/(?P<pk>\d+)/edit$', SelectionUpdate.as_view(), name='selection-edit'),
    url(r'^selection/(?P<pk>\d+)/delete$', SelectionDelete.as_view(), name='selection-delete'),
]
