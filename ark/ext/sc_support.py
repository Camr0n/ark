# --------------------------------------------------------------------------
# This extension adds support for shortcodes to Ark.
#
# Author: Darren Mulholland <dmulholland@outlook.ie>
# License: Public Domain
# --------------------------------------------------------------------------

import ark
import shortcodes
import sys


# Stores an initialized shortcodes.Parser() instance.
scparser = None


# Initialize our shortcode parser on the 'init' event hook.
@ark.hooks.register('init')
def init():

    # Check the site's config file for customized settings for the
    # shortcode parser.
    settings = ark.site.config('shortcodes', {})

    # Initialize a single parser instance.
    global scparser
    scparser = shortcodes.Parser(**settings)


# Filter each record's content on the 'record_text' filter hook and render
# any shortcodes contained in it.
@ark.hooks.register('record_text')
def render(text, record):

    try:
        return scparser.parse(text, record)
    except shortcodes.ShortcodeError as e:
        msg =  "-------------------\n"
        msg += "  Shortcode Error  \n"
        msg += "-------------------\n\n"
        msg += "  Record: %s\n\n" % record['src']
        msg += "  %s: %s" % (e.__class__.__name__, e)
        if e.__context__:
            msg += "\n\nThe following exception was reported:\n\n"
            msg += "%s: %s" % (e.__context__.__class__.__name__, e.__context__)
        sys.exit(msg)
