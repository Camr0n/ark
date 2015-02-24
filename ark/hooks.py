
""" Event and filter hooks for plugins. """


# Maps hook names to lists of handler functions.
_handlers = {}


def register(hook):
    """ Decorator function for registering event and filter handlers. """

    def callback(func):
        _handlers.setdefault(hook, []).append(func)
        return func

    return callback


def event(hook, *args):
    """ Fires an event hook. """
    for func in _handlers.get(hook, []):
        func(*args)


def filter(hook, val, *args):
    """ Fires a filter hook. """
    for func in _handlers.get(hook, []):
        val = func(val, *args)
    return val
