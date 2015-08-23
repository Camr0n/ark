
""" Handles registered template-engine callbacks. """

import sys


# Stores registered template engine callback functions.
_callbacks = []


# Error message if we don't have a registered handler for a page.
errmsg = """Error: no registered template engine for page.

  Page: %s
  Templates: %s"""


def register(callback):
    """ Decorator function for registering template-engine callbacks.

    A template engine callback should accept a page object and return a string
    of html if it chooses to handle it or None if it chooses to decline it. """
    _callbacks.append(callback)
    return callback


def render(page):
    """ Renders the supplied page object into html. """
    for callback in _callbacks:
        html = callback(page)
        if html is not None:
            return html
    sys.exit(errmsg % (page['path'], ', '.join(page['templates'])))

