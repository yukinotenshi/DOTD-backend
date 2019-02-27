from flask import request, redirect
from core.middleware import Middleware
from redis_model import Session


class AuthMiddleware(Middleware):
    def pre_check(self, *args, **kwargs):
        access_token = request.headers.get("Authorization")
        session = Session(access_token)
        session.load()
        username = session.username
        return username is not None

    def default(self):
        return redirect("/")
