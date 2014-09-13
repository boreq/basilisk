class Stack(object):
    """A stack of objects."""

    def __init__(self):
        self._stack = []

    def push(self, obj):
        """Pushes a new item to the stack."""
        self._stack.append(obj)
        return self._stack

    def pop(self):
        """Removes the item from the top of the stack. Returns the removed item
        or `None` if the stack is empty.
        """
        try:
            return self._stack.pop()
        except IndexError:
            return None

    @property
    def top(self):
        """Returns the item at the top of the stack or `None` if the stack is
        empty.
        """
        try:
            return self._stack[-1]
        except IndexError:
            return None


class Proxy(object):
    """Acts as a basic proxy to the object returned by the passed callable."""

    def __init__(self, cal):
        object.__setattr__(self, '_Proxy__cal', cal)

    def _get_object(self):
        return self.__cal()

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self._get_object())
        return getattr(self._get_object(), name)

    def __repr__(self):
        obj = self._get_object()
        return repr(obj)

    __setattr__ = lambda x, n, v: setattr(x._get_object(), n, v)
    __delattr__ = lambda x, n: delattr(x._get_object(), n)
    __str__ = lambda x: str(x._get_object())


