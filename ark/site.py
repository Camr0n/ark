# --------------------------------------------------------------------------
# Loads, processes, and stores the site's configuration data.
# --------------------------------------------------------------------------

import os
import time
import sys

from . import utils


# Stores the site's configuration data.
_config = {}


# Initialize the site model.
def init():

    # Record the start time.
    setconfig('[start]', time.time())

    # Initialize a count of the number of pages rendered.
    setconfig('[rendered]', 0)

    # Initialize a count of the number of pages written to disk.
    setconfig('[written]', 0)

    # Load the site's configuration file.
    load_site_config()


# Attempts to determine the path to the site's home directory.
# Returns an empty string if the directory cannot be located.
def find_home():
    path = os.getcwd()
    while os.path.isdir(path):
        if os.path.isfile(os.path.join(path, '.ark')):
            return os.path.abspath(path)
        path = os.path.join(path, '..')
    return ''


# Attempts to determine the path to the theme directory corresponding to
# the specified theme name. Exits with an error message on failure.
def find_theme(name):

    # A directory in the site's theme library?
    if os.path.isdir(lib(name)):
        return lib(name)

    # A directory in the global theme library?
    if os.getenv('ARK_THEMES'):
        if os.path.isdir(os.path.join(os.getenv('ARK_THEMES'), name)):
            return os.path.join(os.getenv('ARK_THEMES'), name)

    # A raw directory path?
    if os.path.isdir(name):
        return name

    # A bundled theme directory in the application folder?
    bundled = os.path.join(os.path.dirname(__file__), 'ini', 'lib', name)
    if os.path.isdir(bundled):
        return bundled

    sys.exit("Error: cannot locate the theme directory '%s'." % name)


# Returns a value from the site's configuration dictionary.
# If no key is specified, returns the entire dictionary.
# If the key is not found, returns `default`.
def config(key=None, default=None):
    if key:
        return _config.get(key, default)
    else:
        return _config


# Sets a value in the site's configuration dictionary.
def setconfig(key, value):
    _config[key] = value
    return value


# Returns a value from the site's configuration dictionary.
# If the key is not found, sets the key to `default` and returns `default`.
def defconfig(key, default):
    return config(key) or setconfig(key, default)


# Provides access to the site's normalized type-configuration data.
# Returns an entire dictionary of type data if no key is specified.
def typeconfig(id, key=None):
    types = _config.setdefault('[types]', {})

    # Set default values for any missing type data.
    if not id in types:
        types[id] = {
            'id': id,
            'name': utils.titlecase(id),
            'slug': '' if id == 'pages' else utils.slugify(id),
            'tag_slug': 'tags',
            'indexed': False if id == 'pages' else True,
            'order_by': 'date',
            'reverse': True,
            'per_index': 10,
            'per_tag_index': 10,
            'homepage': False,
        }
        types[id].update(config(id, {}))

    if key:
        return types[id][key]
    else:
        return types[id]


# Returns the path to the site's home directory or an empty string if the
# home directory cannot be located. Appends arguments.
def home(*append):
    path = config('[home]') or setconfig('[home]', find_home())
    return os.path.join(path, *append)


# Returns the path to the source directory. Appends arguments.
def src(*append):
    path = config('[src]') or setconfig('[src]', home('src'))
    return os.path.join(path, *append)


# Returns the path to the output directory. Appends arguments.
def out(*append):
    path = config('[out]') or setconfig('[out]', home('out'))
    return os.path.join(path, *append)


# Returns the path to the theme-library directory. Appends arguments.
def lib(*append):
    path = config('[lib]') or setconfig('[lib]', home('lib'))
    return os.path.join(path, *append)


# Returns the path to the extensions directory. Appends arguments.
def ext(*append):
    path = config('[ext]') or setconfig('[ext]', home('ext'))
    return os.path.join(path, *append)


# Returns the path to the includes directory. Appends arguments.
def inc(*append):
    path = config('[inc]') or setconfig('[inc]', home('inc'))
    return os.path.join(path, *append)


# Returns the path to the theme directory. Appends arguments.
def theme(*append):
    path = config('[theme]') or setconfig('[theme]', find_theme(config('theme')))
    return os.path.join(path, *append)


# Returns a list of command-line build-flags.
def flags():
    return config('[flags]', [])


# Returns the output slug list for the specified record type.
def slugs(rectype, *append):
    typeslug = typeconfig(rectype, 'slug')
    sluglist = [typeslug] if typeslug else []
    sluglist.extend(append)
    return sluglist


# Returns the URL corresponding to the specified slug list.
def url(slugs):
    return '@root/' + '/'.join(slugs) + '//'


# Returns the paged URL corresponding to the specified slug list.
def paged_url(slugs, page_number, total_pages):
    if page_number == 1:
        return url(slugs + ['index'])
    elif 2 <= page_number <= total_pages:
        return url(slugs + ['page-%s' % page_number])
    else:
        return ''


# Returns the URL of the index page of the specified record type.
def index_url(rectype):
    if typeconfig(rectype, 'indexed'):
        if typeconfig(rectype, 'homepage'):
            return url(['index'])
        else:
            return url(slugs(rectype, 'index'))
    else:
        return ''


# Returns the record type corresponding to a source path.
def type_from_src(srcpath):
    slugs = os.path.relpath(srcpath, src()).replace('\\', '/').split('/')
    for slug in slugs:
        if slug.startswith('['):
            return slug.strip('[]')


# Returns the output slug list for the specified source directory.
def slugs_from_src(srcdir, *append):
    rectype = type_from_src(srcdir)
    dirnames = os.path.relpath(srcdir, src()).replace('\\', '/').split('/')
    sluglist = slugs(rectype)
    sluglist.extend(utils.slugify(d) for d in dirnames if not d.startswith('['))
    sluglist.extend(append)
    return sluglist


# Returns the name trail for the specified source directory.
def trail_from_src(srcdir):
    rectype = type_from_src(srcdir)
    dirnames = os.path.relpath(srcdir, src()).replace('\\', '/').split('/')
    trail = [typeconfig(rectype, 'name')]
    trail.extend(name for name in dirnames if not name.startswith('['))
    return trail


# Returns the application runtime in seconds.
def runtime():
    return time.time() - config('[start]')


# Increments the count of pages rendered by n and returns the new value.
def rendered(n=0):
    return setconfig('[rendered]', config('[rendered]') + n)


# Increments the count of pages written by n and returns the new value.
def written(n=0):
    return setconfig('[written]', config('[written]') + n)


# Loads and normalizes the site's configuration data.
def load_site_config():

    # Load the default site configuration file.
    path = os.path.join(os.path.dirname(__file__), 'config.py')
    with open(path, encoding='utf-8') as file:
        exec(file.read(), _config)

    # Load the custom site configuration file.
    if home() and os.path.isfile(home('config.py')):
        with open(home('config.py'), encoding='utf-8') as file:
            exec(file.read(), _config)

    # Delete the __builtins__ attribute as it pollutes variable dumps.
    del _config['__builtins__']

    # If 'root' isn't an empty string, make sure it ends in a slash.
    if _config['root'] and not _config['root'].endswith('/'):
        _config['root'] += '/'
