from django.db import models


# Create your models here.

class App(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="应用名称")
    description = models.CharField(max_length=200, verbose_name="应用描述")
    ball_name = models.CharField(null=True, max_length=54, verbose_name="应用包名称")
    http_port = models.IntegerField(null=True, verbose_name="HTTP端口号")
    dubbo_port = models.IntegerField(null=True, verbose_name="DUBBO端口号")

    def __str__(self):
        return self.name


class Env(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="环境名称")
    description = models.CharField(max_length=200, verbose_name="环境描述")

    def __str__(self):
        return self.name


class Host(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="主机名称")
    description = models.CharField(null=True, max_length=200, verbose_name="主机描述")
    ip = models.GenericIPAddressField(protocol='ipv4', null=True, verbose_name="内网IP")
    out_ip = models.GenericIPAddressField(protocol='ipv4', null=True, verbose_name="公网IP")
    env = models.ForeignKey(Env, null=True, on_delete=models.ProtectedError, verbose_name="主机所属环境")
    app = models.ManyToManyField(App, verbose_name="主机和应用关联关系")

    def __str__(self):
        return self.name
