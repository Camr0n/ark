# --------------------------------------------------------------------------
# Handles the site building process.
# --------------------------------------------------------------------------

import os

from . import site
from . import utils
from . import pages
from . import records
from . import tags
from . import hooks


# Builds the site. Copies the site and theme resource files to the output
# directory, then builds the individual record pages, directory index pages,
# and tag index pages.
def build_site():

    # Fire the 'init_build' event.
    hooks.event('init_build')

    # Copy the site's resource files to the output directory, i.e. any files
    # in the site's src directory not inside a [type] directory.
    utils.copydir(site.src(), site.out())

    # Copy the theme's resource files to the output directory.
    if os.path.exists(site.theme('resources')):
        utils.copydir(site.theme('resources'), site.out())

    # Build the individual record pages and directory indexes.
    for path, name in utils.subdirs(site.src()):
        if name.startswith('['):
            build_record_pages(path)
            if site.config('types')[name.strip('[]')]['indexed']:
                build_directory_indexes(path)

    # Build the tag index pages.
    build_tag_indexes()

    # Fire the 'exit_build' event.
    hooks.event('exit_build')


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
    typeconfig = site.config('types')[typeid]

    # Assemble a list of records in this directory and any subdirectories.
    index = []

    # Process subdirectories first.
    for dirinfo in utils.subdirs(dirpath):
        index.extend(build_directory_indexes(dirinfo.path, True))

    # Add any records in this directory to the index.
    for fileinfo in utils.srcfiles(dirpath):
        record = records.record(fileinfo.path)
        if typeconfig['order_by'] in record:
            index.append(record)

    # Are we displaying this index on the homepage?
    if typeconfig['homepage'] and not recursing:
        slugs = []
    else:
        slugs = site.slugs_from_src(dirpath)

    page = pages.IndexPage(
        typeid,
        slugs,
        index,
        typeconfig['per_index']
    )
    page['is_dir_index'] = True
    page['trail'] = site.trail_from_src(dirpath)
    page.render()

    return index


# Creates a paged index for each registered tag.
def build_tag_indexes():

    # Iterate over the site's record types.
    for typeid, recmap in tags.records().items():

        # Fetch the current type's configuration data.
        typeconfig = site.config('types')[typeid]

        # Iterate over the registered tags for the current record type.
        for slug, reclist in recmap.items():

            index = []
            for filepath in reclist:
                record = records.record(filepath)
                if typeconfig['order_by'] in record:
                    index.append(record)

            page = pages.IndexPage(
                typeid,
                tags.slugs(typeid, slug),
                index,
                typeconfig['per_tag_index']
            )
            page['tag'] = tags.names()[typeid][slug]
            page['is_tag_index'] = True
            page['trail'] = [typeconfig['name'], page['tag']]
            page.render()
