# --------------------------------------------------------------------------
# Handles tagging functionality.
# --------------------------------------------------------------------------

from . import site
from .utils import slugify


# Maps tag-slugs to lists of record-filepaths indexed by type.
_rmap = {}


# Maps tag-slugs to tag-names indexed by type.
_nmap = {}


# A TagInfo instance pairs a tag-name with its corresponding tag-index url.
class TagInfo:

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return 'TagInfo(name=%s, url=%s)' % (repr(self.name), repr(self.url))

    def __str__(self):
        return '<a href="%s">%s</a>' % (self.url, self.name)


# Register a new tag mapping.
def register(typeid, tag, filepath):
    _rmap.setdefault(typeid, {}).setdefault(slugify(tag), []).append(filepath)
    _nmap.setdefault(typeid, {}).setdefault(slugify(tag), tag)


# Returns the dictionary of registered tag-to-record mappings.
def records():
    return _rmap


# Returns the dictionary of tag-slug to tag-name mappings.
def names():
    return _nmap


# Returns the output-slug list for the specified tag.
def slugs(typeid, tag, *append):
    typeconfig = site.config('types')[typeid]
    slugs = site.slugs(typeid)
    slugs.extend(s for s in typeconfig['tag_slug'].split('/') if s)
    slugs.append(slugify(tag))
    slugs.extend(append)
    return slugs


# Returns the tag-index url for the specified tag.
def url(typeid, tag):
    return site.url(slugs(typeid, tag, 'index'))
