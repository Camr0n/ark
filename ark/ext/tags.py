# --------------------------------------------------------------------------
# This extension implements Ark's record-tagging functionality.
#
# Author: Darren Mulholland <dmulholland@outlook.ie>
# License: Public Domain
# --------------------------------------------------------------------------

import ark
from ark.utils import slugify


# Maps tag-slugs to lists of record-filepaths indexed by type.
rmap = {}


# Maps tag-slugs to tag-names indexed by type.
nmap = {}


# A Tag instance pairs a tag-name with its corresponding tag-index url.
class Tag:

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return 'Tag(name=%s, url=%s)' % (repr(self.name), repr(self.url))

    def __str__(self):
        return '<a href="%s">%s</a>' % (self.url, self.name)


# Register a callback on the 'record_inst' event hook to process and register
# the record's tags.
@ark.hooks.register('record_inst')
def register_tags(record):
    tags, record['tags'] = record.get('tags', ''), []
    for tag in (t.strip() for t in tags.split(',')):
        if tag:
            register(record['type'], tag, record['src'])
            record['tags'].append(Tag(tag, url(record['type'], tag)))


# Register a callback on the 'build_exit' event hook to build the tag index
# pages.
@ark.hooks.register('build_exit')
def build_tag_indexes():

    # Iterate over the site's record types.
    for typeid, recmap in rmap.items():

        # Fetch the type's configuration data.
        typeconfig = ark.site.typeconfig(typeid)

        # Iterate over the registered tags for the type.
        for slug, filelist in recmap.items():

            reclist = []
            for filepath in filelist:
                record = ark.records.record(filepath)
                if typeconfig['order_by'] in record:
                    reclist.append(record)

            index = ark.pages.Index(
                typeid,
                slugs(typeid, slug),
                reclist,
                typeconfig['per_tag_index']
            )

            index['tag'] = nmap[typeid][slug]
            index['is_tag_index'] = True
            index['trail'] = [typeconfig['name'], nmap[typeid][slug]]

            index.render()


# Register a callback on the 'page_classes' filter to add tag classes.
@ark.hooks.register('page_classes')
def add_tag_classes(classes, page):
    if page.get('is_tag_index'):
        classes.append('tag-index')
        classes.append('tag-index-%s' % slugify(page['tag']))
    return classes


# Register a callback on the 'page_templates' filter to add tag templates.
@ark.hooks.register('page_templates')
def add_tag_templates(templates, page):
    if page.get('is_tag_index'):
        templates = ['%s-tag-index' % page['type']['id'], 'tag-index', 'index']
    return templates


# Register a new tag mapping.
def register(typeid, tag, filepath):
    rmap.setdefault(typeid, {}).setdefault(slugify(tag), []).append(filepath)
    nmap.setdefault(typeid, {}).setdefault(slugify(tag), tag)


# Returns the tag-index url for the specified tag.
def url(typeid, tag):
    return ark.site.url(slugs(typeid, tag, 'index'))


# Returns the output-slug list for the specified tag.
def slugs(typeid, tag, *append):
    slugs = ark.site.slugs(typeid)
    slugs.append(ark.site.typeconfig(typeid, 'tag_slug'))
    slugs.append(slugify(tag))
    slugs.extend(append)
    return slugs
