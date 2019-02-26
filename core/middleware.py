from types import FunctionType


class Middleware:
    def __init__(self, func: FunctionType):
        self.next = func

    def pre_check(self, *args, **kwargs):
        pass

    def default(self):
        pass

    def __call__(self, *args, **kwargs):
        if self.pre_check(*args, **kwargs):
            return self.next(*args, **kwargs)
        else:
            return self.default()
