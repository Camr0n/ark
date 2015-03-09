
""" Loads, processes, and stores the site's configuration data. """

import os
import importlib
import time
import re
import sys

import markdown
import yaml
import syntex
import ibis

from . import utils


# Stores the path to the site's home directory.
_homedir = None

# Stores the path to the site's output directory.
_outdir = None

# Stores the path to the site's theme directory.
_themedir = None

# Stores the site's configuration data.
_config = None

# Stores include strings loaded from the inc directory.
_includes = None

# Stores a list of available template names.
_templates = None

# Stores the build's start time.
_stime = None

# Stores a count of the number of pages rendered.
_pcount = None

# Stores an initialized markdown renderer.
_markdown = None


def init(options):
    """ Called to initialize the site model before building. """

    # Store the start time.
    global _stime
    _stime = time.time()

    # Initialize the page count.
    global _pcount
    _pcount = 0

    # Store the site's home directory.
    global _homedir
    _homedir = options['home']

    # Load the site's configuration data.
    global _config
    _config = _load_site_config()

    # Determine the theme directory.
    global _themedir
    _themedir = _set_theme_dir(options)

    # Determine the output directory.
    global _outdir
    _outdir = options.get('out') or home('out')

    # Determine the urls of the main record-type index pages.
    for typeid in _config['types']:
        _config['types'][typeid]['index_url'] = index_url(typeid)

    # Initialize a markdown renderer.
    global _markdown
    _markdown = markdown.Markdown(**_config.setdefault('markdown', {}))

    # Load and render include strings from the home/inc directory.
    global _includes
    _includes = _load_includes()

    # Assemble a list of available templates.
    global _templates
    _templates = [finfo.base for finfo in utils.files(theme('templates'))]

    # Initialize the template loader.
    ibis.config.loader = ibis.loaders.FileLoader(theme('templates'))

    # Load any extensions we can find.
    _load_extensions()


def home(*append):
    """ Returns the path to the home directory. """
    return os.path.join(_homedir, *append)


def src(*append):
    """ Returns the path to the home/src directory. """
    return home('src', *append)


def out(*append):
    """ Returns the path to the home/out directory. """
    return os.path.join(_outdir, *append)


def theme(*append):
    """ Returns the path to the theme directory. """
    return os.path.join(_themedir, *append)


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


def render(text, ext):
    """ Renders `text` into html using either Syntex or Markdown. """
    if ext.lstrip('.') in ('md', 'markdown'):
        meta = {}
        match = re.match(r"---\n(.*?\n)(---|...)\n", text, re.DOTALL)
        if match:
            text = text[match.end(0):]
            if yaml:
                yaml_meta = yaml.load(match.group(1))
                if isinstance(yaml_meta, dict):
                    meta = yaml_meta
        return _markdown.reset().convert(text), meta
    else:
        return syntex.render(text)


def _load_site_config():
    """ Loads and normalizes the site's configuration data. """

    data, configstr = {}, ''

    # Look for a config.py file in the home directory.
    if os.path.isfile(home('config.py')):
        configstr = open(home('config.py'), encoding='utf-8').read()

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

    # The 'types' dictionary stores configuration data for record types.
    data.setdefault('types', {})

    # Assemble a list of the site's record types from its @type directories.
    types = [
        di.name.lstrip('@')
            for di in utils.subdirs(src())
                if di.name.startswith('@')
    ]

    # Supply default values for any missing type data.
    for typeid in types:
        settings = {
            'name': utils.titlecase(typeid),
            'slug': utils.slugify(typeid),
            'tag_slug': 'tags',
            'indexed': True,
            'order_by': 'datetime',
            'reverse': True,
            'per_index': 10,
            'per_tag_index': 10,
            'homepage': False,
        }
        if typeid == 'pages':
            settings['slug'] = ''
            settings['indexed'] = False
        settings.update(data['types'].get(typeid, {}))
        data['types'][typeid] = settings
        data['types'][typeid]['id'] = typeid

    # Strip any type entries that don't refer to actual @type directories.
    for typeid in list(data['types']):
        if not typeid in types:
            del data['types'][typeid]

    return data


def _load_includes():
    """ Process any text files in the home/inc directory. """
    includes = {}
    if os.path.isdir(home('inc')):
        for finfo in utils.textfiles(home('inc')):
            content = open(finfo.path, encoding='utf-8').read()
            includes[finfo.base], _ = render(content, finfo.ext)
    return includes


def _load_extensions():
    """ Load any Python modules found in the extensions directories. """
    dirpaths = [os.path.join(os.path.dirname(__file__), 'extensions')]
    if os.path.isdir(home('ext')):
        dirpaths.append(home('ext'))
    for dirpath in dirpaths:
        sys.path.insert(0, dirpath)
        names = [
            os.path.splitext(name)[0]
                for name in os.listdir(dirpath)
                    if not name[0] in '_.'
        ]
        for name in names:
            extension = importlib.import_module(name)
        sys.path.pop(0)


def _set_theme_dir(options):
    """ Determines the theme directory to use for the build. """
    theme = options.get('theme') or config('theme') or 'vanilla'
    if os.path.isdir(home('lib')) and theme in os.listdir(home('lib')):
        return home('lib', theme)
    elif theme in os.listdir(os.path.join(os.path.dirname(__file__), 'themes')):
        return os.path.join(os.path.dirname(__file__), 'themes', theme)
    else:
        sys.exit('Error: cannot locate theme directory "%s".' % theme)
