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
    if os.path.exists(site.home('.ark', 'hashes.pickle')):
        with open(site.home('.ark', 'hashes.pickle'), 'rb') as file:
            _hashes['old'] = pickle.load(file)


# Caches page hashes to disk for the next build run.
@hooks.register('exit')
def save():
    if _hashes['new']:
        if not os.path.exists(site.home('.ark')):
            os.makedirs(site.home('.ark'))
        with open(site.home('.ark', 'hashes.pickle'), 'wb') as file:
            pickle.dump(_hashes['new'], file)


# Returns true if filepath is an existing file whose hash matches that of
# the content string.
def match(filepath, content):
    _hashes['new'][filepath] = hashlib.sha1(content.encode()).hexdigest()
    if os.path.exists(filepath):
        return _hashes['old'].get(filepath) == _hashes['new'][filepath]
    else:
        return False
