from flask import Flask
from types import FunctionType


class Router:
    def __init__(self, app: Flask):
        self.app = app
        self.routes = {}

    def group(self, prefix: str, routes: dict, middleware=None):
        for key, value in routes.items():
            method, handler = value
            if middleware:
                handler = middleware(handler)

            if method.lower() == 'get':
                self.get(prefix + key, handler)
            elif method.lower() == 'post':
                self.post(prefix + key, handler)
            elif method.lower() == 'all':
                self.route(prefix + key, handler)

    def get(self, endpoint: str, handler: FunctionType):
        self.routes[(endpoint, 'GET')] = handler

    def post(self, endpoint: str, handler: FunctionType):
        self.routes[(endpoint, 'POST')] = handler

    def route(self, endpoint: str, handler: FunctionType):
        self.routes[(endpoint, 'ALL')] = handler

    def execute(self):
        for key, handler in self.routes.items():
            endpoint, req_type = key
            name = endpoint + req_type
            if req_type == 'POST':
                self.app.route(endpoint, endpoint=name, methods=['POST'])(handler)
            elif req_type == 'ALL':
                self.app.route(endpoint, endpoint=name, methods=['GET', 'POST'])(handler)
            else:
                self.app.route(endpoint, endpoint=name)(handler)
