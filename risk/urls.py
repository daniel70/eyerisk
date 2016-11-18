import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import riskmaps, scenario_list, scenario_edit, scenario_delete, selection_list, selection_delete,\
    selection_create, selection_edit, selection_response, risk_map_list, risk_map_create

urlpatterns = [
    url(r'^$', selection_list, name='risk-home'),
    url(r'^selection/$', selection_list, name='selection-list'),
    url(r'^selection/create$', selection_create, name='selection-add'),
    url(r'^selection/(?P<pk>\d+)/edit$', selection_edit, name='selection-edit'),
    url(r'^selection/(?P<pk>\d+)/delete$', selection_delete, name='selection-delete'),
    url(r'^selection/(?P<pk>\d+)/response$', selection_response, name='selection-response'),

    url(r'^riskmaps/$', riskmaps, name='riskmaps'), #CAN BE DELETED
    url(r'^riskmap/$', risk_map_list, name='risk-map-list'),
    url(r'^riskmap/(?P<pk>\d+)/$', risk_map_list, name='risk-map-list'),
    url(r'^riskmap/create$', risk_map_create, name='risk-map-create'),

    url(r'^scenario/$', scenario_list, name='scenario-list'),
    url(r'^scenario/(?P<pk>\d+)/edit$', scenario_edit, name='scenario-edit'),
    url(r'^scenario/(?P<pk>\d+)/delete$', scenario_delete, name='scenario-delete'),
]
