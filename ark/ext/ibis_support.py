"""
This extension adds support for Ibis templates to Ark.

Author: Darren Mulholland <dmulholland@outlook.ie>
License: Public Domain

"""

import ark
import ibis
import sys


# Initialize our Ibis template loader on the 'init' event hook.
@ark.hooks.register('init')
def init():
    ibis.config.loader = ibis.loaders.FastFileLoader(ark.site.theme('templates'))


# Register our template engine callback for files with a .ibis extension.
@ark.templates.register('ibis')
def callback(page, filename):

    try:
        template = ibis.config.loader(filename)
        return template.render(page)
    except ibis.errors.TemplateError as e:
        msg =  "-----------------------\n"
        msg += "  Ibis Template Error  \n"
        msg += "-----------------------\n\n"
        msg += "  Template: %s\n" % filename
        msg += "  Page:     %s\n\n" % page['path']
        msg += "  %s: %s" % (e.__class__.__name__, e)
        if e.__context__:
            msg += "\n\nThe error was caused by the following exception:\n\n"
            msg += "%s: %s" % (e.__context__.__class__.__name__, e.__context__)
        sys.exit(msg)
