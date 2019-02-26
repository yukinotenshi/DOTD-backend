from flask import request, redirect
from core.middleware import Middleware
from redis_wrapper import RedisClient


redis_client = RedisClient()


class AuthMiddleware(Middleware):
    def pre_check(self, *args, **kwargs):
        access_token = request.headers.get("Authorization")
        username = redis_client.get(access_token)
        return username is not None

    def default(self):
        return redirect("/")
