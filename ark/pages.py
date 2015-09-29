# --------------------------------------------------------------------------
# Handles the creation and rendering of Page objects.
# --------------------------------------------------------------------------

import os
import re
import sys
import math

from . import site
from . import hooks
from . import utils
from . import templates
from . import includes
from . import hashes


# A Page instance represents a single HTML page in the site's output.
class Page(dict):

    # Regex for locating @root/ urls enclosed in quotes or pipes.
    re_url = re.compile(r'''(["'|])@root(/.*?)(#.*?)?\1''')

    def __init__(self, typeid):
        self['flags'] = site.flags()
        self['site'] = site.config()
        self['includes'] = includes.includes()
        self['type'] = site.typeconfig(typeid)
        self['slugs'] = []
        self['record'] = None
        self['records'] = []
        self['trail'] = []
        self['is_single'] = False
        self['is_index'] = False
        self['is_dir_index'] = False
        self['is_homepage'] = False
        self['is_paged'] = False
        self['page'] = 1
        self['total'] = 1
        self['prev_url'] = ''
        self['next_url'] = ''
        self['first_url'] = ''
        self['last_url'] = ''
        self['index_url'] = site.index_url(typeid)

    # Renders the page into HTML and prints the output file.
    def render(self):

        # Fire the 'rendering_page' event.
        hooks.event('rendering_page', self)

        # Generate a string of CSS classes for the page.
        self['classes'] = ' '.join(self._get_class_list())

        # Generate a list of possible template names.
        self['templates'] = self._get_template_list()

        # Determine the output filepath.
        self['path'], depth = self._get_output_filepath()

        # Render the page into html.
        html = templates.render(self)
        site.inc_rendered()

        # Filter the page's html before writing it to disk.
        html = hooks.filter('page_html', html, self)

        # Rewrite all '@root/' urls into their final form.
        html = self._rewrite_urls(html, depth)

        # Write the page to disk. Avoid overwriting identical existing files.
        if not hashes.match(self['path'], html):
            utils.writefile(self['path'], html)
            site.inc_written()

    # Determines the output filepath for the page.
    def _get_output_filepath(self):

        # Directory-style urls require us to append an extra 'index' element.
        slugs = self['slugs'][:]
        if site.config('extension') == '/':
            if slugs[-1] == 'index':
                slugs[-1] = 'index.html'
            else:
                slugs.append('index.html')
        else:
            slugs[-1] = slugs[-1] + site.config('extension')
        filepath = site.out(*slugs)

        if os.path.isfile(os.path.dirname(filepath)):
            msg =  'Filename conflict. '
            msg += 'Attempting to write file and directory with the same name:'
            msg += '\n  ' + os.path.dirname(filepath)
            sys.exit(msg)

        if os.path.isdir(filepath):
            msg =  'Filename conflict. '
            msg += 'Attempting to write file and directory with the same name:'
            msg += '\n  ' + filepath
            sys.exit(msg)

        return filepath, len(slugs)

    def _rewrite_urls(self, html, depth):
        """ Rewrites all @root/ urls to their final form.

        We rewrite all @root/ urls to page-relative form by appending an
        appropriate number of '../' elements.

        Only urls ending in '//' have their endings rewritten to match
        the site's 'extension' configuration setting.

        Note that the native format for links to the homepage is
        '@root/index//', but for convenience we treat the strings '@root/'
        and '@root//' in an identical manner.

        """

        def rewrite_callback(match):
            quote = match.group(1) if match.group(1) in ('"', "'") else ''
            url = match.group(2).lstrip('/')
            if url == '':
                url = 'index//'
            fragment = match.group(3) or ''
            prefix = site.config('root', '') or '../' * (depth - 1)

            if url.endswith('//'):
                url = url.rstrip('/')
                ext = site.config('extension')
                if ext == '/':
                    if url == 'index':
                        if depth == 1:
                            url = '' if fragment else '#'
                        else:
                            url = prefix
                    elif url.endswith('/index'):
                        url = prefix + url[:-5]
                    else:
                        url = prefix + url + '/'
                else:
                    url = prefix + url + ext
            else:
                url = prefix + url

            return '%s%s%s%s' % (quote, url, fragment, quote)

        return self.re_url.sub(rewrite_callback, html)

    # Generates a list of CSS classes for the page.
    def _get_class_list(self):
        classes = [self['type']['id']]

        if self['is_single']:
            classes.append('single')

        if self['is_index']:
            classes.append('index')

        if self['is_dir_index']:
            classes.append('dir-index')

        if self['is_homepage']:
            classes.append('homepage')

        return hooks.filter('page_classes', classes, self)

    # Returns a list of possible template names for the current page.
    def _get_template_list(self):
        templates, typeid = [], self['type']['id']

        # Single record page.
        if self['is_single']:
            if 'template' in self['record']:
                templates.append(self['record']['template'])
            templates.append('%s-single' % typeid)
            templates.append('single')

        # Directory index page.
        elif self['is_dir_index']:
            templates.append('%s-dir-index' % typeid)
            templates.append('dir-index')
            templates.append('index')

        # Fallback on the index template.
        else:
            templates.append('index')

        return hooks.filter('page_templates', templates, self)


# A RecordPage represents a single-record page.
class RecordPage(Page):

    def __init__(self, record):
        Page.__init__(self, record['type'])
        self['record'] = record
        self['slugs'] = record['slugs']
        self['is_single'] = True
        self['is_homepage'] = (record['slugs'] == ['index'])


# An Index represents a collection of index pages.
class Index:

    def __init__(self, typeid, slugs, records, recs_per_page):

        # Sort the records.
        records.sort(
            key = lambda rec: rec[site.typeconfig(typeid, 'order_by')],
            reverse = site.typeconfig(typeid, 'reverse')
        )

        # How many pages do we need?
        recs_per_page = recs_per_page or len(records) or 1
        total_pages = math.ceil(float(len(records)) / recs_per_page)

        # Create the individual pages.
        self.pages = []
        for i in range(1, total_pages + 1):
            page = Page(typeid)

            page['records'] = records[recs_per_page * (i - 1):recs_per_page * i]
            page['is_index'] = True
            page['is_paged'] = (total_pages > 1)
            page['page'] = i
            page['total'] = total_pages

            page['first_url'] = site.paged_url(slugs, 1, total_pages)
            page['prev_url'] = site.paged_url(slugs, i - 1, total_pages)
            page['url'] = site.paged_url(slugs, i, total_pages)
            page['next_url'] = site.paged_url(slugs, i + 1, total_pages)
            page['last_url'] = site.paged_url(slugs, total_pages, total_pages)

            page['slugs'] = slugs[:]
            if i == 1:
                page['slugs'].append('index')
            else:
                page['slugs'].append('page-%s' % i)

            page['is_homepage_index'] = (len(page['slugs']) == 1)
            page['is_homepage'] = (page['slugs'] == ['index'])

            self.pages.append(page)

    def __setitem__(self, key, value):
        for page in self.pages:
            page[key] = value

    def render(self):
        for page in self.pages:
            page.render()
