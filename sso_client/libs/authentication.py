# coding: utf8
import requests
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from sso_client.libs import utils
from sso_client.models import User

SESSION_KEY = '_auth_user_id'


class SessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user_id = request.session.get(SESSION_KEY)
        if not user_id:
            return None
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive")
        token = request.session.get("USER_TOKEN")
        if not token:
            return None
        headers = {utils.SSO_TMP_TOKEN_HEADER: token}
        res = requests.get(utils.get_sso_api_url("myself"), headers=headers)
        if res.status_code != 200 or res.json()["code"] != 200:
            request.session.clear()
            return None
        return user, None


class TicketAuthentication(BaseAuthentication):
    keyword = utils.TICKET_AUTHENTICATION_PARAMETER_NAME
    is_active_key = 'is_active'
    key = None

    def process_request(self):
        url = "{}?ticket={}".format(utils.get_sso_api_url("get_token_by_ticket"), self.key)
        return requests.get(url)

    def get_user_dict(self, res_json):
        return res_json["data"]["user"]

    def authenticate(self, request):
        ticket = request.GET.get(self.keyword)
        if not ticket:
            return None
        self.key = ticket
        user, res_json = self.authenticate_credentials()
        request.session[SESSION_KEY] = user.id
        request.session["USER_TOKEN"] = res_json["data"]["token"]
        return user, None

    def authenticate_credentials(self):
        res = self.process_request()
        if res.status_code == 200:
            if not res.json()["code"] == 200:
                raise exceptions.AuthenticationFailed(res.json()["msg"])
            user_dict = self.get_user_dict(res.json())
            try:
                user = User.objects.get(username=user_dict["username"])
            except User.DoesNotExist:
                user = User()
                user.username = user_dict['username']
                user.cname = user_dict['cname']
                user.email = user_dict['email']
                user.save()
            return user, res.json()
        else:
            raise exceptions.AuthenticationFailed()

    def authenticate_header(self, request):
        return self.keyword


class TokenAuthentication(TicketAuthentication):
    keyword = utils.SSO_ACCESS_TOKEN_HEADER
    is_active_key = 'is_active'

    def process_request(self):
        url = utils.get_sso_api_url("myself")
        headers = {utils.SSO_ACCESS_TOKEN_HEADER: self.key}
        return requests.get(url, headers=headers)

    def get_user_dict(self, res_json):
        return res_json["data"]

    def authenticate(self, request):
        access_token = utils.get_token(request, self.keyword)
        if not access_token:
            return None
        self.key = access_token
        return self.authenticate_credentials()

    def authenticate_header(self, request):
        return self.keyword
