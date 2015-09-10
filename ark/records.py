# --------------------------------------------------------------------------
# Handles the creation and caching of Record objects.
# --------------------------------------------------------------------------

import os
import re
import datetime

from . import utils
from . import site
from . import hooks
from . import renderers


# Stores an in-memory cache of record objects.
_cache = {}


# Returns the Record object corresponding to the specified source file.
def record(filepath):
    if not filepath in _cache:
        _cache[filepath] = Record(filepath)
    return _cache[filepath]


class Record(dict):

    """ A record object represents a parsed source file.

    Record objects should not be instantiated directly. Instead use the
    `record()` function to take advantage of caching.

    """

    def __init__(self, filepath):

        # Parse the filepath.
        dirpath = os.path.dirname(filepath)
        fileinfo = utils.fileinfo(filepath)

        # Load the record file.
        text, meta = utils.load(filepath)
        self.update(meta)

        # Add the default set of record attributes.
        self['type']  = site.type_from_src(dirpath)
        self['slug']  = meta.get('slug') or utils.slugify(fileinfo.base)
        self['slugs'] = site.slugs_from_src(dirpath, self['slug'])
        self['src']   = filepath
        self['ext']   = fileinfo.ext
        self['url']   = site.url(self['slugs'])

        # Add a default datetime stamp. We use the 'date' attribute if it's
        # present, otherwise we use the file creation time (OSX, BSD, Windows)
        # or the time of the file's last metadata change (Linux).
        date = self.get('date')
        if isinstance(date, datetime.datetime):
            self['date'] = date
        elif isinstance(date, datetime.date):
            self['date'] = datetime.datetime.fromordinal(date.toordinal())
        else:
            self['date'] = utils.get_creation_time(filepath)

        # Filter the record's text content. (Shortcodes are processed here.)
        self['text'] = hooks.filter('record_text', text, self)

        # Render the record's content into html.
        html = renderers.render(self['text'], fileinfo.ext)

        # Filter the record's html content.
        self['html'] = hooks.filter('record_html', html, self)

        # Fire the 'record_inst' event. (Tags are processed here.)
        hooks.event('record_inst', self)
