# coding: utf8
import functools
import json

from django.core.cache import cache

from sso_client.libs.response import ApiResponse


def cache_response(timeout=60):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(view_cls, request, *args, **kwargs):
            cache_key_prefix = request.path.replace('/', '_')
            user = getattr(request, 'user', None)
            if user:
                cache_key = "{}_{}".format(cache_key_prefix, user.username)
                cache_value = cache.get(cache_key)
                response = func(view_cls, request, *args, **kwargs)
                if not cache_value:
                    data = {
                        "status_code": response.status_code,
                        "data": response.data,
                    }
                    cache.set(cache_key, json.dumps(data), timeout)
                else:
                    data = json.loads(cache_value)
                    response = ApiResponse(data=data["data"])
                    response.status_code = data["status_code"]
                return response
            return func(view_cls, request, *args, **kwargs)

        return wrapper

    return decorator
