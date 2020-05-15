# coding: utf8
from rest_framework import exceptions
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from sso_client.libs import utils
from sso_client.libs.authentication import SessionAuthentication, TicketAuthentication, TokenAuthentication
from sso_client.libs.exception import api_exception_handler
from sso_client.libs.permissions import CheckUserPermission
from sso_client.libs.response import ApiResponse


def format_response(response):
    data = {
        "code": response.status_code,
        "msg": "ok",
        "data": response.data,
    }
    response.data = data
    return response


def check_pk_is_exist(model, pk_list):
    model_name = model.__name__.lower()
    if isinstance(pk_list, list):
        for pk in pk_list:
            try:
                model.objects.get(id=pk)
            except model.DoesNotExist:
                raise exceptions.ParseError("{} id {} does not exist".format(model_name, pk))
            except Exception as e:
                raise exceptions.ParseError("invalid {} id {}".format(model_name, pk))
    else:
        raise exceptions.ParseError("parameter {} is null or not a list".format(model_name))


def extend_many_to_many_url(request, obj, related_obj, serializer_class):
    related_mode = serializer_class.Meta.model
    serializer = serializer_class(related_obj.all().order_by("id"), many=True)
    if request.method == "GET":
        return ApiResponse(data=serializer.data)
    elif request.method in ["POST", "PUT"]:
        pk_list = request.data.get("id")
        check_pk_is_exist(related_mode, pk_list)
        related_obj.set(pk_list)
    else:
        related_obj.clear()
    obj.save()
    return ApiResponse(msg="process success", data=serializer.data)


def get_end_url_path(url_path):
    path_list = url_path.split('/')
    return path_list[-2] if url_path.endswith('/') else path_list[-1]


class AuthenticationView(APIView):
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    authentication_classes = [SessionAuthentication, TicketAuthentication, TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_exception_handler(self):
        return api_exception_handler


class PermissionView(AuthenticationView):
    permission_classes = (CheckUserPermission,)
    app_name = utils.SSO_CLIENT_APP_NAME

    @property
    def resource_name(self):
        return self.__class__.__name__.replace('ViewSet', '')


class BaseView(PermissionView, ModelViewSet):
    uk_name_list = ['name']
    model = None
    error_msg = None
    authenticate_permission_path = None

    def get_old_obj(self, uk_name, uk_value):
        kwargs = {uk_name: uk_value}
        return self.model.objects.get(**kwargs)

    def check_uk_is_exist(self, request, action_type):
        self.model = self.get_serializer().Meta.model
        for uk_name in self.uk_name_list:
            try:
                uk_value = request.data.get(uk_name)
                self.error_msg = "{}: {} already exist.".format(uk_name, uk_value)
                old_obj = self.get_old_obj(uk_name, uk_value)
                if action_type == "create":
                    raise exceptions.ParseError(detail=self.error_msg)
                else:
                    if old_obj != self.get_object():
                        raise exceptions.ParseError(detail=self.error_msg)
            except self.model.DoesNotExist:
                pass
        return False

    def list(self, request, *args, **kwargs):
        return format_response(super().list(request, *args, **kwargs))

    def retrieve(self, request, *args, **kwargs):
        return format_response(super().retrieve(request, *args, **kwargs))

    def create(self, request, *args, **kwargs):
        self.check_uk_is_exist(request, "create")
        return format_response(super().create(request, *args, **kwargs))

    def update(self, request, *args, **kwargs):
        self.check_uk_is_exist(request, "update")
        return format_response(super().update(request, *args, **kwargs))

    def destroy(self, request, *args, **kwargs):
        return format_response(super().destroy(request, *args, **kwargs))

    # 重新设置权限级别，指定的URL允许通过认证的用户即可访问
    def get_permissions(self):
        if self.authenticate_permission_path and (
                get_end_url_path(self.request.path) in self.authenticate_permission_path):
            return [IsAuthenticated()]
        return super().get_permissions()
