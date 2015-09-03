# --------------------------------------------------------------------------
# This extension adds syntex support to Ark.
#
# Files with a .stx extension will be rendered as syntex.
#
# Author: Darren Mulholland <dmulholland@outlook.ie>
# License: Public Domain
# --------------------------------------------------------------------------

import ark
import syntex


# Register our callback to render files with a .stx extension.
@ark.renderers.register('stx')
def render(text):
    html, _ = syntex.render(text)
    return html
