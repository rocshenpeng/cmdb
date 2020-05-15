# coding: utf8
import requests
from django.conf import settings
from rest_framework import exceptions

SSO_SERVER_API_URL = getattr(settings, "SSO_SERVER_API_URL")
SSO_CLIENT_APP_NAME = getattr(settings, "SSO_CLIENT_APP_NAME")
SSO_ACCESS_TOKEN_HEADER = getattr(settings, "SSO_ACCESS_TOKEN_HEADER", "access-token")
SSO_TMP_TOKEN_HEADER = getattr(settings, "SSO_TMP_TOKEN_HEADER", "tmp-token")
TICKET_AUTHENTICATION_PARAMETER_NAME = getattr(settings, "TICKET_AUTHENTICATION_PARAMETER_NAME", "ticket")
DEFAULT_CACHE_USER_INFO_TIMEOUT = 60

SSO_API_URL_MAP = {
    "get_token_by_ticket": "/get_token_by_ticket",
    "myself": "/user/myself/",
    "check_permission": "/user/has_permission/",
    "get_permission": "/user/permission/",
    "my_menu": "/menu/my_menu/",
}


def get_sso_api_url(url_key):
    return "{}{}".format(SSO_SERVER_API_URL, SSO_API_URL_MAP[url_key])


def get_token(request, token_head):
    token_header_name = 'HTTP_{}'.format(token_head.replace('-', '_').upper())
    return request.META.get(token_header_name)


def process_sso_api_request(request, url):
    token = get_token(request, SSO_ACCESS_TOKEN_HEADER)
    header_name = SSO_ACCESS_TOKEN_HEADER
    if not token:
        header_name = SSO_TMP_TOKEN_HEADER
        token = request.session.get("USER_TOKEN")
        if not token:
            raise exceptions.NotAuthenticated()
    return requests.get(url, headers={header_name: token})


def get_param_or_exception(request, key):
    if request.method == "GET":
        params_dict = request.GET
    else:
        params_dict = request.data
    value = params_dict.get(key)
    if not value:
        raise exceptions.ParseError("parameter {} is required".format(key))
    return value


def get_obj_or_exception(model, pk_id=None, uk_name=None):
    msg_suffix = "id or name"
    try:
        if pk_id:
            msg_suffix = "id {}".format(pk_id)
            return model.objects.get(id=pk_id)
        elif uk_name:
            msg_suffix = "name {}".format(uk_name)
            return model.objects.get(name=uk_name)
    except model.DoesNotExist:
        raise exceptions.ParseError("invalid {} {}".format(model.__name__.lower(), msg_suffix))


def get_obj_by_request_param(request, model, param_id=None, param_name=None):
    pk_id = uk_name = None
    if param_id:
        pk_id = get_param_or_exception(request, param_id)
    elif param_name:
        uk_name = get_param_or_exception(request, param_name)
    return get_obj_or_exception(model, pk_id=pk_id, uk_name=uk_name)
