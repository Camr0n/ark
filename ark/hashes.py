# --------------------------------------------------------------------------
# Handles the file hashing mechanism.
# --------------------------------------------------------------------------

import os
import hashlib
import pickle

from . import site
from . import hooks


# Stores page hashes from the previous and current build runs.
_hashes = { 'old': {}, 'new': {} }


# Loads cached page hashes from the last build run.
@hooks.register('init')
def load():
    if os.path.isfile(site.home('.ark')):
        if os.path.getsize(site.home('.ark')) > 0:
            with open(site.home('.ark'), 'rb') as file:
                unpickled = pickle.load(file)
                _hashes['old'] = unpickled['hashes']


# Caches page hashes to disk for the next build run.
# We fake the file mtime in case the .ark file has been checked into
# a version control repository.
@hooks.register('exit')
def save():
    if _hashes['new']:
        atime = os.path.getatime(site.home('.ark'))
        mtime = os.path.getmtime(site.home('.ark'))
        with open(site.home('.ark'), 'wb') as file:
            pickle.dump(dict(hashes=_hashes['new']), file)
        os.utime(site.home('.ark'), (atime, mtime))


# Returns true if filepath is an existing file whose hash matches that of
# the content string. We use the relative filepath as the key to avoid
# leaking potentially sensitive information (e.g. usernames) if the hash
# file is checked into a public version control repository.
def match(filepath, content):
    key = os.path.relpath(filepath, site.out())
    _hashes['new'][key] = hashlib.sha1(content.encode()).hexdigest()
    if os.path.exists(filepath):
        return _hashes['old'].get(key) == _hashes['new'][key]
    else:
        return False
