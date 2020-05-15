# coding: utf8
from django.conf.urls import url
from sso_client.views import user

urlpatterns = [
    url(r'login$', user.login),
    url(r'logout$', user.logout),
    url(r'menu/$', user.MenuView.as_view()),
]