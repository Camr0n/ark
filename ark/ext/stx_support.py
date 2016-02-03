# --------------------------------------------------------------------------
# This extension adds Syntex support to Ark.
#
# Files with a .stx extension will be rendered as Syntex.
#
# Author: Darren Mulholland <darren@mulholland.xyz>
# License: Public Domain
# --------------------------------------------------------------------------

import ark
import syntex


# Register our callback to render files with a .stx extension.
@ark.renderers.register('stx')
def render(text):
    html, _ = syntex.render(text)
    return html
