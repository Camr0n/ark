"""
This extension adds support for Jinja templates to Ark.

Author: Darren Mulholland <dmulholland@outlook.ie>
License: Public Domain

"""

import ark
import jinja2
import sys


# Stores an initialized Jinja environment instance.
env = None


# Initialize our Jinja environment on the 'init' event hook.
@ark.hooks.register('init')
def init():

    # Initialize a template loader.
    settings = {
        'loader': jinja2.FileSystemLoader(ark.site.theme('templates'))
    }

    # Check the site's config file for any custom settings.
    settings.update(ark.site.config('jinja', {}))

    # Initialize an Environment instance.
    global env
    env = jinja2.Environment(**settings)


# Register our template engine callback for files with a .jinja extension.
@ark.templates.register('jinja')
def callback(page, filename):

    # Load the template object.
    try:
        template = env.get_template(filename)
    except jinja2.TemplateError as e:
        msg =  'Jinja template error loading file: %s\n\n' % filename
        msg += '  %s: %s' % (e.__class__.__name__, e)
        if e.__context__:
            msg += '\n\n  %s: %s' % (
                e.__context__.__class__.__name__, e.__context__
            )
        sys.exit(msg)

    # Render the page.
    try:
        return template.render(page)
    except jinja2.TemplateError as e:
        msg =  'Jinja template error rendering page:\n'
        msg += '  %s\n\n' % page['path']
        msg += '  %s: %s' % (e.__class__.__name__, e)
        if e.__context__:
            msg += '\n\n  %s: %s' % (
                e.__context__.__class__.__name__, e.__context__
            )
        sys.exit(msg)
