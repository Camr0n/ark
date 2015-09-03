# --------------------------------------------------------------------------
# Handles template-engine callbacks.
# --------------------------------------------------------------------------

import sys

from . import site
from . import utils


# Maps file extensions to their registered template engine callbacks.
_callbacks = {}


# Stores a cached list of the theme's template files.
_templates = None


def register(ext):
    """ Decorator function for registering template-engine callbacks.

    A template-engine callback should accept a page object and a
    template filename and return a string of html.

    Callbacks are registered per file extension, e.g.

    @ark.templates.register('ibis')
    def callback(filepath, page):
        ...
        return html

    """

    def register_callback(callback):
        _callbacks[ext] = callback
        return callback

    return register_callback


# Renders the supplied page object into html.
def render(page):

    # Cache a list of the theme's template files for future calls.
    global _templates
    if _templates is None:
        _templates = utils.files(site.theme('templates'))

    # Find the first template file matching the page's template list.
    for name in page['templates']:
        for finfo in _templates:
            if name == finfo.base:
                if finfo.ext in _callbacks:
                    return _callbacks[finfo.ext](page, finfo.name)
                else:
                    sys.exit(
                        "Error: unrecognised template extension '.%s'." % finfo.ext
                    )

    # Missing template file. Print an error message and exit.
    sys.exit(
        "Error: missing template file.\n\n  Page: %s\n  Templates: %s" % (
            page['path'], ', '.join(page['templates'])
        )
    )
