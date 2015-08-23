
""" Handles the main site building process. """

import os

from . import site
from . import utils
from . import pages
from . import records
from . import tags
from . import hooks


def build(options):
    """ Builds the site. Accepts a dictionary of command line options. """

    # Initialize the site model.
    site.init(options)

    # Fire the 'init' event. (Runs callbacks registered on the 'init' hook.)
    hooks.event('init')

    # Copy the site's resource files to the output directory, i.e. any files
    # in the site's src directory not inside a [type] directory.
    utils.copydir(site.src(), site.out())

    # Copy the theme's resource files to the output directory.
    if os.path.exists(site.theme('resources')):
        utils.copydir(site.theme('resources'), site.out())

    # Build the individual record pages and directory indexes.
    for dirpath, dirname in utils.subdirs(site.src()):
        if dirname.startswith('['):
            build_record_pages(dirpath)
            if site.config('types')[dirname.strip('[]')]['indexed']:
                build_directory_indexes(dirpath)

    # Build the tag index pages.
    build_tag_indexes()

    # Cleanup actions before exiting.
    site.exit()

    # Fire the 'exit' event. (Runs callbacks registered on the 'exit' hook.)
    hooks.event('exit')


def build_record_pages(dirpath):
    """ Creates an HTML page for each record file in the source directory. """

    for fileinfo in utils.srcfiles(dirpath):
        record = records.record(fileinfo.path)
        page = pages.RecordPage(record)
        page.render()

    for dirinfo in utils.subdirs(dirpath):
        build_record_pages(dirinfo.path)


def build_directory_indexes(dirpath, recursing=False):
    """ Creates a paged index for each directory of records. """

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
    if typeconfig['homepage'] and not recursing :
        slugs = []
    else:
        slugs = site.slugs_from_src(dirpath)

    page = pages.IndexPage(
        typeid,
        slugs,
        index,
        typeconfig['per_index']
    )
    page['flags']['is_dir_index'] = True
    page['trail'] = site.trail_from_src(dirpath)
    page.render()

    return index


def build_tag_indexes():
    """ Creates a paged index for each registered tag. """

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
            page['flags']['is_tag_index'] = True
            page['trail'] = [typeconfig['name'], page['tag']]
            page.render()
