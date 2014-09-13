from .context import Stack, Proxy


_env_context_stack = Stack()


def _get_current_env():
    env = _env_context_stack.top
    if env is None:
        raise Exception('Not in the context.')
    return env


current_env = Proxy(_get_current_env)
