# coding: utf8
import json

from django.core.cache import cache
from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from sso_client.libs import utils

permission_key_prefix = "user_permission"

request_method_action_maps = {
    'options': 'read',
    'get': 'read',
    'post': 'add',
    'put': 'update',
    'patch': 'update',
    'delete': 'delete'
}


def get_user_permissions(request, app_name):
    permission_key = "{}_{}".format(permission_key_prefix, request.user.id)
    cache_value = cache.get(permission_key)
    if cache_value:
        user_permission_list = json.loads(cache_value)
    else:
        url = "{}?app_name={}".format(utils.get_sso_api_url("get_permission"), app_name)
        res = utils.process_sso_api_request(request, url)
        if res.status_code == 200:
            if res.json()["code"] == 200:
                user_permission_list = res.json()["data"]
                cache.set(permission_key, json.dumps(user_permission_list), utils.DEFAULT_CACHE_USER_INFO_TIMEOUT)
            else:
                raise exceptions.PermissionDenied(res.json()["msg"])
        else:
            raise exceptions.PermissionDenied("get user permission from sso server failed.")
    return user_permission_list


class CheckUserPermission(BasePermission):
    def has_permission(self, request, view):
        # 检测用户是否登录
        user = getattr(request, 'user', None)
        if not (user and user.is_authenticated):
            raise exceptions.NotAuthenticated
        app_name = getattr(view, 'app_name')
        resource_name = getattr(view, 'resource_name')
        action_map = request_method_action_maps.get(request.method.lower())
        permission_name = "{}{}".format(action_map, resource_name)
        if permission_name in get_user_permissions(request, app_name):
            return True
        raise exceptions.PermissionDenied("permission deny")
