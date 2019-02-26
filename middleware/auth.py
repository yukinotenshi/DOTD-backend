from flask import request, redirect
from core.middleware import Middleware


class AuthMiddleware(Middleware):
    def pre_check(self, *args, **kwargs):
        return request.headers.get('Authorization') == 'RANDOM API KEY'

    def default(self):
        return redirect('/')
