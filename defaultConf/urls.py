"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.conf.urls import url
from django.urls import include

from sso_client.libs.response import PageNotFoundResponse, ServerErrorResponse

urlpatterns = [
    url(r'^cmdb/api/', include('core.urls')),
    url(r'^cmdb/', include('sso_client.urls')),
]


def page_not_found(request, *args, **kwargs):
    return PageNotFoundResponse(msg="Invalid request path: {}".format(request.path))


def page_server_error(request, *args, **kwargs):
    return ServerErrorResponse()


handler404 = page_not_found
handler500 = page_server_error
