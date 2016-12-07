import django.contrib.auth.urls
from django.conf.urls import url, include
from .views import riskmaps, scenario_list, scenario_edit, scenario_delete, selection_list, selection_delete,\
    selection_create, selection_edit, selection_response, risk_map_list, risk_map_create, risk_map_create_category, \
    no_company, risk_map_delete, impact_list, settings, department_create, department_edit, department_delete

urlpatterns = [
    url(r'^$', selection_list, name='risk-home'),
    url(r'^no_company$', no_company, name='no-company'),
    url(r'^selection/$', selection_list, name='selection-list'),
    url(r'^selection/create$', selection_create, name='selection-add'),
    url(r'^selection/(?P<pk>\d+)/edit$', selection_edit, name='selection-edit'),
    url(r'^selection/(?P<pk>\d+)/delete$', selection_delete, name='selection-delete'),
    url(r'^selection/(?P<pk>\d+)/response$', selection_response, name='selection-response'),

    url(r'^risk_maps/$', riskmaps, name='riskmaps'), #CAN BE DELETED
    url(r'^risk_map/$', risk_map_list, name='risk-map-list'),
    url(r'^risk_map/(?P<pk>\d+)/$', risk_map_list, name='risk-map-list'),
    url(r'^risk_map/create$', risk_map_create, name='risk-map-create'),
    url(r'^risk_map/create-category$', risk_map_create_category, name='risk-map-create-category'),
    url(r'^risk_map/(?P<pk>\d+)/delete', risk_map_delete, name='risk-map-delete'),

    url(r'^scenario/$', scenario_list, name='scenario-list'),
    url(r'^scenario/(?P<pk>\d+)/edit$', scenario_edit, name='scenario-edit'),
    url(r'^scenario/(?P<pk>\d+)/delete$', scenario_delete, name='scenario-delete'),

    url(r'^impact/$', impact_list, name='impact-list'),

    url(r'^settings/$', settings, name='settings'),

    url(r'^department/create$', department_create, name='department-add'),
    url(r'^department/(?P<pk>\d+)/edit$', department_edit, name='department-edit'),
    url(r'^department/(?P<pk>\d+)/delete$', department_delete, name='department-delete'),

]
