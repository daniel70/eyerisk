import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import SelectionDetail, SelectionControlAssess, \
    SelectionControlView, ControlSelectionView, control_selection, control_selection_react, \
    riskmaps, scenario_list, scenario_edit, scenario_delete, selection_list, selection_delete, selection_create, \
    selection_edit, selection_response

urlpatterns = [
    url(r'^$', selection_list, name='risk-home'),
    url(r'^selection/$', selection_list, name='selection-list'),
    url(r'^selection/(?P<pk>\d+)/$', SelectionDetail.as_view(), name='selection-detail'),
    url(r'^selection/create$', selection_create, name='selection-add'),
    # url(r'^selection/create$', SelectionCreate.as_view(), name='selection-add'),
    # url(r'^selection/(?P<pk>\d+)/edit$', SelectionUpdate.as_view(), name='selection-edit'),
    url(r'^selection/(?P<pk>\d+)/edit$', selection_edit, name='selection-edit'),
    url(r'^selection/(?P<pk>\d+)/delete$', selection_delete, name='selection-delete'),
    url(r'^selection/(?P<pk>\d+)/response$', selection_response, name='selection-response'),
    url(r'^selectioncontrol/(?P<pk>\d+)/$', SelectionControlView.as_view(), name='selection-control'),
    url(r'^controlselection/(?P<pk>\d+)/$', control_selection, name='control-selection'),
    url(r'^controlselectionreact/(?P<pk>\d+)/$', control_selection_react, name='control-selection-react'),
    # url(r'^controlselection/(?P<pk>\d+)/$', ControlSelectionView.as_view(), name='control-selection'),
    url(r'^selectioncontrol/(?P<selection_id>\d+)/assess$', SelectionControlAssess.as_view(), name='selection-assess'),

    url(r'^riskmaps/$', riskmaps, name='riskmaps'),

    url(r'^scenario/$', scenario_list, name='scenario-list'),
    url(r'^scenario/(?P<pk>\d+)/edit$', scenario_edit, name='scenario-edit'),
    url(r'^scenario/(?P<pk>\d+)/delete$', scenario_delete, name='scenario-delete'),
]

