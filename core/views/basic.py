# coding: utf8
from rest_framework.decorators import action

from core.models import App, Env, Host
from core.serializer import AppSerializer, EnvSerializer, HostSerializer
from sso_client.libs.response import ApiResponse
from sso_client.views.basic import BaseView, extend_many_to_many_url
from sso_client.libs import utils


def modify_obj_relation(request, obj, relation_objs, relation_obj_serializer, param_id):
    tmp_relation_obj = utils.get_obj_by_request_param(request, relation_obj_serializer.Meta.model, param_id=param_id)
    if request.method == 'DELETE':
        if tmp_relation_obj in relation_objs.all():
            relation_objs.remove(tmp_relation_obj)
            obj.save()
    else:
        if tmp_relation_obj not in relation_objs.all():
            relation_objs.add(tmp_relation_obj)
            obj.save()
    return ApiResponse(data=relation_obj_serializer(relation_objs.all().order_by("id"), many=True).data)


class ExtendAppView:
    def get_app_related_obj(self):
        raise NotImplementedError("you must override this function")

    @action(detail=True, methods=["GET", "POST", "PUT", "DELETE"])
    def app(self, request, pk=None):
        return extend_many_to_many_url(request, self.get_object(), self.get_app_related_obj(), AppSerializer)


class ExtendHostView:
    def get_host_related_obj(self):
        raise NotImplementedError("you must override this function")

    @action(detail=True, methods=["GET", "POST", "PUT", "DELETE"])
    def host(self, request, pk=None):
        return extend_many_to_many_url(request, self.get_object(), self.get_host_related_obj(), HostSerializer)

    @action(detail=True, methods=["POST", "PUT", "DELETE"])
    def modify_host_relation(self, request, pk=None):
        return modify_obj_relation(request, self.get_object(), self.get_object().host_set, HostSerializer, "host_id")


class AppViewSet(BaseView, ExtendHostView):
    queryset = App.objects.all()
    serializer_class = AppSerializer

    def get_host_related_obj(self):
        return self.get_object().host_set


class EnvViewSet(BaseView, ExtendAppView, ExtendHostView):
    queryset = Env.objects.all()
    serializer_class = EnvSerializer

    def get_app_related_obj(self):
        hosts = self.get_object().host_set.all()
        app = App.objects.filter(host__in=hosts)
        return app

    # 重写app方法，仅支持GET查询
    @action(detail=True, methods=["GET"])
    def app(self, request, pk=None):
        return super().app(request, pk=pk)

    def get_host_related_obj(self):
        return self.get_object().host_set


class HostViewSet(BaseView, ExtendAppView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

    def get_app_related_obj(self):
        return self.get_object().app

    @action(detail=False, methods=["GET"])
    def get_host_by_app_and_env(self, request):
        app = utils.get_obj_by_request_param(request, App, param_name="app_name")
        env = utils.get_obj_by_request_param(request, Env, param_name="env_name")
        host_list = Host.objects.filter(env=env).filter(app=app)
        return ApiResponse(data=HostSerializer(host_list, many=True).data)

    @action(detail=True, methods=["POST", "PUT", "DELETE"])
    def modify_app_relation(self, request, pk=None):
        return modify_obj_relation(request, self.get_object(), self.get_object().app, AppSerializer, "app_id")
