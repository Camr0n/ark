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
    setconfig('[starttime]', time.time())

    # Locate the site's home directory.
    setconfig('[homedir]', locate_home())

    # Load the site's configuration data.
    load_site_config()

    # Locate the theme directory.
    setconfig('[themedir]', locate_theme(config('theme')))

    # Set the output directory.
    setconfig('[outdir]', home('out'))

    # Initialize a count of the number of pages rendered.
    setconfig('[rendered]', 0)

    # Initialize a count of the number of pages written to disk.
    setconfig('[written]', 0)


# Attempts to determine the path to the site's home directory.
# Exits with an error message on failure.
def locate_home():
    path = os.getcwd()
    while os.path.isdir(path):
        if os.path.exists(os.path.join(path, 'src')):
            return os.path.abspath(path)
        path = os.path.join(path, '..')
    sys.exit("Error: cannot locate the site's home directory.")


# Attempts to determine the path to the theme directory corresponding to
# the specified theme name. Exits with an error message on failure.
def locate_theme(name):

    # A directory in the site's theme library?
    if os.path.isdir(home('lib', name)):
        return home('lib', name)

    # A directory in the global theme library?
    if os.getenv('ARK_THEMES'):
        if os.path.isdir(os.path.join(os.getenv('ARK_THEMES'), name)):
            return os.path.join(os.getenv('ARK_THEMES'), name)

    # A raw directory path?
    if os.path.isdir(name):
        return name

    # A bundled theme directory in the application folder?
    bundled = os.path.join(os.path.dirname(__file__), 'init', 'lib', name)
    if os.path.isdir(bundled):
        return bundled

    sys.exit("Error: cannot locate the theme directory '%s'." % name)


# Returns a value from the site's configuration dictionary.
# Returns the entire dictionary if no key is specified.
def config(key=None, fallback=None):
    """ Returns the dictionary of site configuration data. """
    if key:
        return _config.get(key, fallback)
    else:
        return _config


# Sets a value in the site's configuration dictionary.
def setconfig(key, value):
    _config[key] = value


# Returns the path to the site's home directory.
def home(*append):
    return os.path.join(config('[homedir]'), *append)


# Returns the path to the site's src directory.
def src(*append):
    return home('src', *append)


# Returns the path to the output directory.
def out(*append):
    return os.path.join(config('[outdir]'), *append)


# Returns the path to the theme directory.
def theme(*append):
    return os.path.join(config('[themedir]'), *append)


# Returns a list of command line build flags.
def flags():
    return config('[flags]', [])


# Returns the output slug list for the specified record type.
def slugs(typeid, *append):
    typeslug = config('types')[typeid]['slug']
    sluglist = [slug for slug in typeslug.split('/') if slug]
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
def index_url(typeid):
    if config('types')[typeid]['indexed']:
        if config('types')[typeid]['homepage']:
            return url(['index'])
        else:
            return url(slugs(typeid, 'index'))
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
    typeid = type_from_src(srcdir)
    dirnames = os.path.relpath(srcdir, src()).replace('\\', '/').split('/')
    sluglist = slugs(typeid)
    sluglist.extend(utils.slugify(d) for d in dirnames if not d.startswith('['))
    sluglist.extend(append)
    return sluglist


# Returns the name trail for the specified source directory.
def trail_from_src(srcdir):
    typeid = type_from_src(srcdir)
    dirnames = os.path.relpath(srcdir, src()).replace('\\', '/').split('/')
    trail = [config('types')[typeid]['name']]
    trail.extend(name for name in dirnames if not name.startswith('['))
    return trail


# Returns the run time in seconds.
def runtime():
    return time.time() - config('[starttime]')


# Returns the count of pages rendered.
def rendered():
    return config('[rendered]')


# Increments the count of pages rendered.
def inc_rendered():
    setconfig('[rendered]', config('[rendered]') + 1)


# Returns the count of pages written.
def written():
    return config('[written]')


# Increments the count of pages written.
def inc_written():
    setconfig('[written]', config('[written]') + 1)


# Loads and normalize the site's configuration data.
def load_site_config():

    # Load the default site configuration file.
    path = os.path.join(os.path.dirname(__file__), 'config.py')
    with open(path, encoding='utf-8') as file:
        exec(file.read(), _config)

    # Load the custom site configuration file.
    if os.path.isfile(home('config.py')):
        with open(home('config.py'), encoding='utf-8') as file:
            exec(file.read(), _config)

    # Delete the __builtins__ attribute as it pollutes variable dumps.
    del _config['__builtins__']

    # If 'root' isn't an empty string, make sure it ends in a slash.
    if _config['root'] and not _config['root'].endswith('/'):
        _config['root'] += '/'

    # The 'types' dictionary stores configuration data for record types.
    _config.setdefault('types', {})

    # Assemble a list of the site's record types from its [type] directories.
    types = [di.name.strip('[]')
                for di in utils.subdirs(src())
                    if di.name.startswith('[')]

    # Supply default values for any missing data.
    for id in types:
        data = {
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
        data.update(_config['types'].get(id, {}))
        _config['types'][id] = data
        _config['types'][id]['index_url'] = index_url(id)
