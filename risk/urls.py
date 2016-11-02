import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import SelectionDetail, SelectionList, SelectionCreate, SelectionUpdate, SelectionControlAssess, \
    SelectionDelete, SelectionControlView, ControlSelectionView, control_selection, control_selection_react, \
    riskmaps, scenarios


urlpatterns = [
    url(r'^$', SelectionList.as_view(), name='risk-home'),
    url(r'^selection/$', SelectionList.as_view(), name='selection-list'),
    url(r'^selection/(?P<pk>\d+)/$', SelectionDetail.as_view(), name='selection-detail'),
    url(r'^selection/create$', SelectionCreate.as_view(), name='selection-add'),
    url(r'^selection/(?P<pk>\d+)/edit$', SelectionUpdate.as_view(), name='selection-edit'),
    url(r'^selection/(?P<pk>\d+)/delete$', SelectionDelete.as_view(), name='selection-delete'),
    url(r'^selectioncontrol/(?P<pk>\d+)/$', SelectionControlView.as_view(), name='selection-control'),
    url(r'^controlselection/(?P<pk>\d+)/$', control_selection, name='control-selection'),
    url(r'^controlselectionreact/(?P<pk>\d+)/$', control_selection_react, name='control-selection-react'),
    # url(r'^controlselection/(?P<pk>\d+)/$', ControlSelectionView.as_view(), name='control-selection'),
    url(r'^selectioncontrol/(?P<selection_id>\d+)/assess$', SelectionControlAssess.as_view(), name='selection-assess'),

    url(r'^riskmaps/$', riskmaps, name='riskmaps'),
    url(r'^scenarios/$', scenarios, name='scenarios'),
    url(r'^scenarios/(?P<simple>T)/$', scenarios, name='simple_scenarios'),
]

