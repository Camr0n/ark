
""" Handles the creation and caching of Record objects. """

import os
import re
import datetime

from . import utils
from . import site
from . import tags


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

        # Assume all input is utf-8 encoded.
        dirpath, filename = os.path.split(filepath)
        base, ext = os.path.splitext(filename)
        text = open(filepath, encoding='utf-8').read()

        # Render the file's text content as html.
        html, meta = site.render(text, ext)
        for key, value in meta.items():
            self[key.lower().replace(' ', '_')] = value

        # The filename gives us our default url slug.
        slug = self.get('slug') or utils.slugify(base)

        # Add our basic record attributes.
        self['content'] = html
        self['type'] = site.type_from_src(dirpath)
        self['slugs'] = site.slugs_from_src(dirpath, slug)
        self['url'] = site.url(self['slugs'])

        # Convert `date` objects to `datetime` objects.
        dtime = self.get('datetime') or self.get('date')
        if isinstance(dtime, datetime.datetime):
            self['datetime'] = dtime
        elif isinstance(dtime, datetime.date):
            self['datetime'] = datetime.datetime.fromordinal(dtime.toordinal())

        # Process the record's tag list, if present.
        taglist, self['tags'] = self.get('tags', ''), []
        for tag in (t.strip() for t in taglist.split(',')):
            if tag:
                tags.register(self['type'], tag, filepath)
                url = tags.url(self['type'], tag)
                self['tags'].append(tags.TagInfo(tag, url))
