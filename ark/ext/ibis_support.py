"""
This extension adds support for Ibis templates to Ark.

Author: Darren Mulholland <dmulholland@outlook.ie>
License: Public Domain

"""

import ark
import ibis


# Register our template engine callback. This function accepts a page object
# and renders it into html. A template engine callback should return the html
# string if it has handled the page object or None if it has declined it.
# Here we handle page objects for which a template file with a .html or a .ibis
# extension is available.
@ark.templates.register
def callback(page):
    for name in page['templates']:
        template = try_load_template(name + '.html', name + '.ibis')
        if template:
            return render(template, page)
    return None


# Initialize our Ibis template loader on the 'init' event hook.
@ark.hooks.register('init')
def init():
    ibis.config.loader = ibis.loaders.FastFileLoader(ark.site.theme('templates'))


# Loop through the supplied list of filenames and try to load a corresponding
# template for each. Return the first template if successful, otherwise None.
def try_load_template(*filenames):
    for filename in filenames:
        try:
            return ibis.config.loader(filename)
        except ibis.errors.LoadError:
            continue
        except ibis.errors.TemplateError as e:
            msg =  'Ibis template error loading file:\n'
            msg += '  %s\n\n' % filename
            msg += '  %s: %s' % (e.__class__.__name__, e)
            if e.__context__:
                msg += '\n\n  %s: %s' % (
                    e.__context__.__class__.__name__, e.__context__
                )
            sys.exit(msg)
    return None


# Renders the page object into html.
def render(template, page):
    try:
        html = template.render(page)
    except ibis.errors.TemplateError as e:
        msg =  'Ibis template error rendering page:\n'
        msg += '  %s\n\n' % page['path']
        msg += '  %s: %s' % (e.__class__.__name__, e)
        if e.__context__:
            msg += '\n\n  %s: %s' % (
                e.__context__.__class__.__name__, e.__context__
            )
        sys.exit(msg)
    return html
