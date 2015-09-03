# --------------------------------------------------------------------------
# Event and filter hooks.
# --------------------------------------------------------------------------

# Maps hook names to lists of callback functions.
_handlers = {}


# Decorator function for registering event and filter handlers.
def register(hook):

    def callback(func):
        _handlers.setdefault(hook, []).append(func)
        return func

    return callback


# Fires an event hook.
def event(hook, *args):
    for func in _handlers.get(hook, []):
        func(*args)


# Fires a filter hook.
def filter(hook, value, *args):
    for func in _handlers.get(hook, []):
        value = func(value, *args)
    return value
