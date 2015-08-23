
""" Handles text-to-html rendering-engine callbacks. """

import sys


# Maps file extensions to their registered rendering engine callbacks.
# We include null renderers for files with a .txt or .html extension.
# These can be overridden by registered callbacks if desired.
_renderers = {
    'txt': lambda s: s,
    'html': lambda s: s,
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


def render(text, ext):
    """ Renders `text` and returns the result. """
    if ext in _renderers:
        return _renderers[ext](text)
    else:
        sys.exit("Error: no registered renderer for the '.%s' extension." % ext)
