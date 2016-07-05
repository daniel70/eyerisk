import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import SelectionDetail, SelectionList, SelectionCreate, SelectionUpdate, SelectionControlAssess, \
    SelectionDelete, StandardViewSet, SelectionViewSet, ControlDomainViewSet, SelectionControlViewSet, \
    SelectionControlView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'standards', StandardViewSet)
router.register(r'selections', SelectionViewSet)
router.register(r'controldomains', ControlDomainViewSet)
router.register(r'selectioncontrols', SelectionControlViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^$', SelectionList.as_view(), name='risk-home'),
    url(r'^selection/$', SelectionList.as_view(), name='selection-list'),
    url(r'^selection/(?P<pk>\d+)/$', SelectionDetail.as_view(), name='selection-detail'),
    url(r'^selection/create$', SelectionCreate.as_view(), name='selection-add'),
    url(r'^selection/(?P<pk>\d+)/edit$', SelectionUpdate.as_view(), name='selection-edit'),
    url(r'^selection/(?P<pk>\d+)/delete$', SelectionDelete.as_view(), name='selection-delete'),
    url(r'^selectioncontrol/(?P<pk>\d+)/$', SelectionControlView.as_view(), name='selection-control'),
    # url(r'^selectioncontrol/(?P<selection_id>\d+)/assess$', SelectionControlAssess.as_view(), name='selection-assess'),

]
