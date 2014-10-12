"""
This module loads, processes, and stores the site's configuration data.

"""

import os
import importlib
import time

from . import utils

from .lib import syntex
from .lib import flock


# Stores the site's input and output directories.
_dirs = None

# Stores the site's configuration data.
_config = None

# Stores include strings loaded from the source directory.
_includes = None

# Stores a list of available template names.
_templates = None

# Stores the build's start time.
_stime = None

# Stores a count of the number of pages rendered.
_pcount = None


def init(srcdir, dstdir, themedir):
    """ Called to initialize the site model before building. """

    # Store the start time.
    global _stime
    _stime = time.time()

    # Initialize the page count.
    global _pcount
    _pcount = 0

    # Store the input and output directories for future lookups.
    global _dirs
    _dirs = (srcdir, dstdir, themedir)

    # Load the site's configuration.
    global _config
    _config = _load_site_config(srcdir)

    # Determine the urls of the main record-type index pages.
    for typeid in _config['types']:
        _config['types'][typeid]['index_url'] = index_url(typeid)

    # Load ~include strings from the source directory.
    global _includes
    _includes = _load_includes(srcdir)

    # Assemble a list of available templates.
    global _templates
    _templates = [finfo.base for finfo in utils.files(theme('templates'))]

    # Initialize the template loader.
    flock.config.loader = flock.loaders.FileLoader(theme('templates'))

    # Load plugins from the plugins directory.
    _load_plugins()


def src(*append):
    """ Returns the path to the source directory. """
    return os.path.join(_dirs[0], *append)


def dst(*append):
    """ Returns the path to the destination directory. """
    return os.path.join(_dirs[1], *append)


def theme(*append):
    """ Returns the path to the theme directory. """
    return os.path.join(_dirs[2], *append)


def templates():
    """ Returns the list of available template names. """
    return _templates


def includes():
    """ Returns the dictionary of processed include strings. """
    return _includes


def type(typeid):
    """ Returns the specified dictionary of type configuration data. """
    return _config['types'][typeid.lstrip('@')]


def config(key=None, fallback=None):
    """ Returns the dictionary of site configuration data. """
    if key:
        return _config.get(key, fallback)
    else:
        return _config


def slugs(typeid, *append):
    """ Returns the output slug list for the specified record type. """
    typeslug = _config['types'][typeid]['slug']
    sluglist = [slug for slug in typeslug.split('/') if slug]
    sluglist.extend(append)
    return sluglist


def url(slugs):
    """ Returns the URL corresponding to the specified slug list. """
    return '@root/' + '/'.join(slugs) + '//'


def paged_url(slugs, page_number, total_pages):
    """ Returns the paged URL corresponding to the specified slug list. """
    if page_number == 1:
        return url(slugs + ['index'])
    elif 2 <= page_number <= total_pages:
        return url(slugs + ['page-%s' % page_number])
    else:
        return ''


def index_url(typeid):
    """ Returns the URL of the index page of the specified record type. """
    if _config['types'][typeid]['indexed']:
        if _config['types'][typeid]['homepage']:
            return url(['index'])
        else:
            return url(slugs(typeid, 'index'))
    else:
        return ''


def build_time():
    """ Returns the current build time in seconds. """
    return time.time() - _stime


def page_count():
    """ Returns the current page count. """
    return _pcount


def increment_page_count():
    """ Increments the page count. """
    global _pcount
    _pcount += 1


def type_from_src(srcpath):
    """ Determines the record type from the source path. """
    slugs = os.path.relpath(srcpath, src()).replace('\\', '/').split('/')
    for slug in slugs:
        if slug.startswith('@'):
            return slug.lstrip('@')


def slugs_from_src(srcdir, *append):
    """ Returns the output slug list for the specified source directory. """
    typeid = type_from_src(srcdir)
    dirnames = os.path.relpath(srcdir, src()).replace('\\', '/').split('/')
    sluglist = slugs(typeid)
    sluglist.extend(utils.slugify(d) for d in dirnames if not d.startswith('@'))
    sluglist.extend(append)
    return sluglist


def trail_from_src(srcdir):
    """ Returns the name trail for the specified source directory. """
    typeid = type_from_src(srcdir)
    dirnames = os.path.relpath(srcdir, src()).replace('\\', '/').split('/')
    trail = [_config['types'][typeid]['name']]
    trail.extend(dname for dname in dirnames if not dname.startswith('@'))
    return trail


def _load_site_config(srcdir):
    """ Loads and normalizes the site's configuration data. """

    data, configstr = {}, ''

    # Look for a config.py file in the source directory.
    # Also check one directory level up.
    if os.path.isfile(src('config.py')):
        configstr = open(src('config.py'), encoding='utf-8').read()
    elif os.path.isfile(src('../config.py')):
        configstr = open(src('../config.py'), encoding='utf-8').read()

    # Evaluate the file contents as a string of Python code.
    if configstr:
        exec(configstr, data)
        del data['__builtins__']

    # Set a default extension for generated files.
    # The extension can be an empty string, an arbitrary file extension,
    # or a forward slash for directory-style urls.
    data.setdefault('extension', '.html')

    # If a root has been supplied, make sure it ends with a trailing slash.
    # The root string can be a full url (http://example.com/), a single
    # slash (/), or an empty string (the default) for page relative urls.
    if data.setdefault('root', '') and not data['root'].endswith('/'):
        data['root'] += '/'

    # The 'types' dictionary stores configuration data for each entry type.
    data.setdefault('types', {})

    # Get a list of the types this site is using.
    types = [
        di.name.lstrip('@')
            for di in utils.subdirs(srcdir)
                if di.name.startswith('@')
    ]

    # Supply default values for any missing type data.
    for typeid in types:
        defaults = {
            "name": utils.titlecase(typeid),
            "slug": '' if typeid == 'pages' else utils.slugify(typeid),
            "tag_slug": "tags",
            "indexed": False if typeid == 'pages' else True,
            "order_by": "datetime",
            "reverse": True,
            "per_index": 10,
            "per_tag_index": 10,
            "homepage": False,
        }
        defaults.update(data['types'].get(typeid, {}))
        data['types'][typeid] = defaults
        data['types'][typeid]['id'] = typeid

    # Strip any type entries that don't refer to actual source directories.
    for typeid in list(data['types']):
        if not typeid in types:
            del data['types'][typeid]

    return data


def _load_includes(source):
    """ Process any files in the ~includes directory. """
    includes = {}
    if os.path.isdir(src('~includes')):
        for finfo in utils.files(src('~includes')):
            content = open(finfo.path, encoding='utf-8').read()
            includes[finfo.base], _ = syntex.render(content)
    return includes


def _load_plugins():
    """ Load any plugins found in the plugins directory. """
    pdir = os.path.join(os.path.dirname(__file__), 'plugins')
    pnames = [
        os.path.splitext(name)[0]
            for name in os.listdir(pdir)
                if not name.startswith('__')
    ]
    for pname in pnames:
        plugin = importlib.import_module('.plugins.' + pname, 'malt')
        if hasattr(plugin, 'init'):
            plugin.init()
