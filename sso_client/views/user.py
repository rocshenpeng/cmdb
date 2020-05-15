# coding: utf8
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view

from sso_client.libs import utils
from sso_client.libs.decorator import cache_response
from sso_client.libs.response import ApiResponse
from sso_client.views.basic import AuthenticationView


def login(request):
    print(request.environ)
    print(request.get_host())
    print(request.get_port())
    print(request.is_secure())
    print(request.get_full_path_info())
    return ApiResponse(msg="login")


@api_view(["GET"])
def logout(request):
    request.session.clear()
    return ApiResponse(msg="logout success")


class MenuView(AuthenticationView):
    @cache_response()
    def get(self, request):
        url = "{}?app_name={}".format(utils.get_sso_api_url("my_menu"), utils.SSO_CLIENT_APP_NAME)
        res = utils.process_sso_api_request(request, url)
        data = {"code": res.status_code, "msg": "ok", "data": ""}
        if res.status_code == 200:
            data = res.json()
        else:
            data["msg"] = "get menu from sso server error."
        return ApiResponse(msg=data["msg"], code=data["code"], data=data["data"])
