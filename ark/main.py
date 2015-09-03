# --------------------------------------------------------------------------
# Application entry point.
# --------------------------------------------------------------------------

from . import site
from . import hooks
from . import extensions


# Calling main() initializes the site model, loads the site's plugins, and
# fires a series of event hooks. All functionality is handled by extensions
# registering callbacks on these hooks.
def main():

    # Initialize the site model.
    site.init()

    # Load extensions.
    extensions.load()

    # Fire the 'init' event. (Runs callbacks registered on the 'init' hook.)
    hooks.event('init')

    # Fire the 'main' event. (Runs callbacks registered on the 'main' hook.)
    hooks.event('main')

    # Fire the 'exit' event. (Runs callbacks registered on the 'exit' hook.)
    hooks.event('exit')
