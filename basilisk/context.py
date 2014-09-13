from .globals import _env_context_stack


class EnvContext(object):

    def __init__(self, env):
        self.env = env

    def push(self):
        _text_stack.push(self)

    def pop(self):
        rv = _text_stack.pop()
        if not rv is self:
            raise ValueError('Popped wrong context.')

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.pop()
