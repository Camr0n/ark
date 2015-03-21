
""" Handles all tagging functionality. """

from . import site
from .utils import slugify


# Maps tag-slugs to lists of record-filepaths indexed by type.
_rmap = {}

# Maps tag-slugs to tag-names indexed by type.
_nmap = {}


class TagInfo:

    """ Pairs a tag-name with its corresponding tag-index url. """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return 'TagInfo(name=%s, url=%s)' % (repr(self.name), repr(self.url))

    def __str__(self):
        return '<a href="%s">%s</a>' % (self.url, self.name)


def register(typeid, tag, filepath):
    """ Register a new tag mapping. """
    _rmap.setdefault(typeid, {}).setdefault(slugify(tag), []).append(filepath)
    _nmap.setdefault(typeid, {}).setdefault(slugify(tag), tag)


def records():
    """ Returns the dictionary of registered tag-to-record mappings. """
    return _rmap


def names():
    """ Returns the dictionary of tag-slug-to-tag-name mappings. """
    return _nmap


def slugs(typeid, tag, *append):
    """ Returns the output-slug list for the specified tag. """
    slugs = site.slugs(typeid)
    slugs.extend(s for s in site.type(typeid)['tag_slug'].split('/') if s)
    slugs.append(slugify(tag))
    slugs.extend(append)
    return slugs


def url(typeid, tag):
    """ Returns the index-page url for the specified tag. """
    return site.url(slugs(typeid, tag, 'index'))
