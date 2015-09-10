# --------------------------------------------------------------------------
# Handles text-to-html rendering-engine callbacks.
# --------------------------------------------------------------------------

import sys


# Maps file extensions to their registered rendering engine callbacks.
# We include a set of null renderers for various common file extensions.
# These can be overridden by registered callbacks if desired.
_renderers = {
    'css': lambda s: s,
    'html': lambda s: s,
    'js': lambda s: s,
    'txt': lambda s: s,
}


def register(ext):

    """ Decorator function for registering rendering-engine callbacks.

    A rendering-engine callback should accept a string of text and return
    a string containing the rendered result.

    Callbacks are registered per file extension, e.g.

        @ark.renderers.register('md')
        def callback(text):
            ...
            return rendered

    """

    def register_callback(callback):
        _renderers[ext] = callback
        return callback

    return register_callback


# Renders a string and returns the result.
def render(text, ext):
    if ext in _renderers:
        return _renderers[ext](text)
    else:
        sys.exit("Error: no registered renderer for the '.%s' extension." % ext)
