# --------------------------------------------------------------------------
# Handles the file hashing mechanism.
#
# Before writing a page file to disk we check if there is an existing
# file of the same name left over from a previous build. If there is,
# we compare the hash of the new page's content with the cached hash
# of the old page's content. If they are identical, we skip writing the
# new page to disk.
#
# This has two effects:
#
#   * We save on disk IO, which is more expensive than comparing hashes.
#   * We avoid unnecessarily bumping the file modification time.
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
    if os.path.isfile(site.home('.arkcache', 'hashes.pickle')):
        with open(site.home('.arkcache', 'hashes.pickle'), 'rb') as file:
            _hashes['old'] = pickle.load(file)


# Caches page hashes to disk for the next build run.
@hooks.register('exit')
def save():
    if _hashes['new']:
        if not os.path.isdir(site.home('.arkcache')):
            os.makedirs(site.home('.arkcache'))
        with open(site.home('.arkcache', 'hashes.pickle'), 'wb') as file:
            pickle.dump(_hashes['new'], file)


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
