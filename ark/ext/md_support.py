# --------------------------------------------------------------------------
# This extension adds Markdown support to Ark.
#
# Files with a .md extension will be rendered as Markdown.
#
# Author: Darren Mulholland <darren@mulholland.xyz>
# License: Public Domain
# --------------------------------------------------------------------------

import ark
import markdown


# Stores an initialized markdown renderer.
mdrenderer = None


# Initialize our markdown renderer on the 'init' event hook.
@ark.hooks.register('init')
def init():

    # Check the site's config file for customized settings for the
    # markdown renderer.
    settings = ark.site.config('markdown', {})

    # Initialize a markdown renderer.
    global mdrenderer
    mdrenderer = markdown.Markdown(**settings)


# Register our callback to render files with a .md extension.
@ark.renderers.register('md')
def render(text):
    return mdrenderer.reset().convert(text)
