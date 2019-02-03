"""eyerisk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import logout
from two_factor.urls import urlpatterns as tf_urls
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls
from rest_framework import routers
# from risk import views as riskviews
from risk import api

router = routers.DefaultRouter()
router.register(r'selection', api.SelectionViewSet, base_name='Selection')
router.register(r'riskmap', api.RiskMapViewSet, base_name='Risk Map')


urlpatterns = [
    url(r'^', include('risk.urls')),
    url(r'^risk/', include('risk.urls')),
    url(r'^api/', include(router.urls)),
    # url(r'^api/', include(router.urls, namespace='api')),
    # url(r'^api-auth/', include('rest_framework.urls')), WE SHOULD NOT CREATE ANOTHER ATTACK SURFACE !!!
    url(r'', include(tf_urls)),
    url(r'', include(tf_twilio_urls)),
    url(r'^account/logout/$', view=logout, name='logout'),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
