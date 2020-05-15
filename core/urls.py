# coding: utf8
from django.conf.urls import url
from django.urls import include
from rest_framework import routers
from core.views.basic import AppViewSet, EnvViewSet, HostViewSet

router = routers.DefaultRouter()
router.register('app', AppViewSet)
router.register('env', EnvViewSet)
router.register('host', HostViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]
