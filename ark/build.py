# --------------------------------------------------------------------------
# Handles the site building process.
# --------------------------------------------------------------------------

import os

from . import site
from . import utils
from . import pages
from . import records
from . import hooks


# Builds the site.
#
#   1. Copies the site and theme resource files to the output directory.
#   2. Builds the individual record pages.
#   3. Builds the directory index pages.
#
def build_site():

    # Fire the 'build_init' event.
    hooks.event('build_init')

    # Copy the site's resource files to the output directory, i.e. any files
    # in the site's src directory not inside a [type] directory.
    utils.copydir(site.src(), site.out())

    # Copy the theme's resource files to the output directory.
    if os.path.exists(site.theme('resources')):
        utils.copydir(site.theme('resources'), site.out(), onlyolder=False)

    # Build the individual record pages and directory indexes.
    for path, name in utils.subdirs(site.src()):
        if name.startswith('['):
            build_record_pages(path)
            if site.typeconfig(name.strip('[]'), 'indexed'):
                build_directory_indexes(path)

    # Fire the 'build_exit' event.
    hooks.event('build_exit')


# Creates a HTML page for each record file in the source directory.
def build_record_pages(dirpath):

    for fileinfo in utils.srcfiles(dirpath):
        record = records.record(fileinfo.path)
        page = pages.RecordPage(record)
        page.render()

    for dirinfo in utils.subdirs(dirpath):
        build_record_pages(dirinfo.path)


# Creates a paged index for each directory of records.
def build_directory_indexes(dirpath, recursing=False):

    # Determine the record type from the directory path.
    typeid = site.type_from_src(dirpath)

    # Fetch the type's configuration data.
    typeconfig = site.typeconfig(typeid)

    # Assemble a list of records in this directory and any subdirectories.
    reclist = []

    # Process subdirectories first.
    for dirinfo in utils.subdirs(dirpath):
        reclist.extend(build_directory_indexes(dirinfo.path, True))

    # Add any records in this directory to the index.
    for fileinfo in utils.srcfiles(dirpath):
        record = records.record(fileinfo.path)
        if typeconfig['order_by'] in record:
            reclist.append(record)

    # Are we displaying this index on the homepage?
    if typeconfig['homepage'] and not recursing:
        slugs = []
    else:
        slugs = site.slugs_from_src(dirpath)

    # Create and render the set of index pages.
    index = pages.Index(typeid, slugs, reclist, typeconfig['per_index'])
    index['is_dir_index'] = True
    index['trail'] = site.trail_from_src(dirpath)
    index.render()

    return reclist
