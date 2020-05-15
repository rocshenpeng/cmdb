from django.db import models


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=100, unique=True, verbose_name="用户登录名")
    cname = models.CharField(max_length=100, verbose_name="用户显示名")
    email = models.EmailField(max_length=100, verbose_name="邮箱")
    is_active = models.BooleanField(default=True, verbose_name="用户是否可用")
    last_login = models.DateTimeField(blank=True, null=True, verbose_name="最后登录时间")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['cname', 'email']

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.username
