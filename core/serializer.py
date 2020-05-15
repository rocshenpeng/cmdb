# coding: utf8
from rest_framework.serializers import ModelSerializer

from core.models import App, Host, Env


class AppSerializer(ModelSerializer):
    class Meta:
        model = App
        fields = ['id', 'name', 'description', 'ball_name', 'http_port', 'dubbo_port']


class EnvSerializer(ModelSerializer):
    class Meta:
        model = Env
        fields = ['id', 'name', 'description']


class HostSerializer(ModelSerializer):
    class Meta:
        model = Host
        fields = ['id', 'name', 'ip', 'out_ip', 'description', 'env']
