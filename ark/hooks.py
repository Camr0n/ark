# --------------------------------------------------------------------------
# Event and filter hooks.
# --------------------------------------------------------------------------

# Maps hook names to lists of callback functions indexed by order.
_handlers = {}


# Decorator function for registering event and filter handlers.
def register(hook, order=0):

    def register_handler(func):
        _handlers.setdefault(hook, {}).setdefault(order, []).append(func)
        return func

    return register_handler


# Fires an event hook.
def event(hook, *args):
    for order in sorted(_handlers.get(hook, {})):
        for func in _handlers[hook][order]:
            func(*args)


# Fires a filter hook.
def filter(hook, value, *args):
    for order in sorted(_handlers.get(hook, {})):
        for func in _handlers[hook][order]:
            value = func(value, *args)
    return value
