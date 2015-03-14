
""" Handles the creation and caching of Record objects. """

import os
import re
import datetime

from . import utils
from . import site
from . import tags
from . import hooks


# Stores an in-memory cache of record objects.
_cache = {}


def record(filepath):
    """ Returns the Record object corresponding to the specified text file. """
    if not filepath in _cache:
        _cache[filepath] = Record(filepath)
    return _cache[filepath]


class Record(dict):

    """ Represents a parsed text file.

    Record objects should not be instantiated directly. Instead use the
    `record()` function to take advantage of caching.

    """

    def __init__(self, filepath):

        # Load the record file.
        text, meta, format = site.load(filepath)
        self.update(meta)

        # The filename gives us the default url slug.
        dirpath, filename = os.path.split(filepath)
        basename, _ = os.path.splitext(filename)

        # Add default record attributes.
        self['slug'] = meta.get('slug') or utils.slugify(basename)
        self['file'] = filepath
        self['path'] = site.slugs_from_src(dirpath, self['slug'])
        self['type'] = site.type_from_src(dirpath)
        self['form'] = format
        self['url']  = site.url(self['path'])

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

        # Process the record's tag list, if present.
        taglist, self['tags'] = self.get('tags', ''), []
        for tag in (t.strip() for t in taglist.split(',')):
            if tag:
                tags.register(self['type'], tag, filepath)
                url = tags.url(self['type'], tag)
                self['tags'].append(tags.TagInfo(tag, url))

        # Process any shortcodes in the record's content.
        self['text'] = hooks.filter(
            'record_text',
            site.parse_shortcodes(text, self, filepath),
            self
        )

        # Render the record's content into html.
        self['html'] = hooks.filter(
            'record_html',
            site.render(self['text'], format),
            self
        )
