
""" Handles the creation and rendering of Page objects. """

import os
import re
import sys
import math

import ibis

from . import site
from . import hooks
from . import utils


class Page(dict):

    """ Represents an HTML page. """

    # Regex for locating @root/ urls enclosed in quotes or pipes.
    re_url = re.compile(r'''(["'|])@root(/.*?)(#.*?)?\1''')

    def __init__(self, type):
        self['site'] = site.config()
        self['includes'] = site.includes()
        self['type'] = site.type(type)
        self['slugs'] = []
        self['record'] = None
        self['records'] = []
        self['trail'] = []
        self['tag'] = ''
        self['flags'] = {
            'is_single': False,
            'is_index': False,
            'is_dir_index': False,
            'is_tag_index': False,
            'is_homepage': False,
        }
        self['paging'] = {
            'is_paged': False,
            'page': 1,
            'total': 1,
            'prev_url': '',
            'next_url': '',
            'first_url': '',
            'last_url': '',
        }

    def render(self):
        """ Renders the page into HTML and prints the output file. """

        # Generate css classes for the body element.
        self._set_css_classes()

        # Determine the template to use.
        self._set_template()

        # Fire the 'render_page' event.
        hooks.event('rendering_page', self)

        # Determine the output filepath. Directory-style URLs require
        # us to add an extra 'index' element to the path.
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

        # Load the template.
        try:
            template = ibis.config.loader(self['template'])
        except ibis.errors.TemplateError as e:
            msg =  'Error loading template file:\n'
            msg += '  %s\n\n' % self['template']
            msg += '  %s: %s' % (e.__class__.__name__, e)
            if e.__context__:
                msg += '\n\n  %s: %s' % (
                    e.__context__.__class__.__name__, e.__context__
                )
            sys.exit(msg)

        # Render the page into html.
        try:
            html = template.render(self)
            site.increment_pages_rendered()
        except ibis.errors.TemplateError as e:
            msg =  'Template error rendering file:\n'
            msg += '  %s\n\n' % filepath
            msg += '  %s: %s' % (e.__class__.__name__, e)
            if e.__context__:
                msg += '\n\n  %s: %s' % (
                    e.__context__.__class__.__name__, e.__context__
                )
            sys.exit(msg)

        # Rewrite all '@root/' urls into their final form.
        html = self._rewrite_urls(html, len(slugs))

        # Write the page to disk. Avoid overwriting identical existing files.
        if not site.hashmatch(filepath, html):
            utils.writefile(filepath, html)
            site.increment_pages_written()

    def _rewrite_urls(self, html, depth):
        """ Rewrite all @root/ urls to their final form.

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

    def _set_css_classes(self):
        """ Assembles a set of CSS classes for the <body> element. """

        classes = [self['type']['id']]

        if self['flags']['is_single']:
            classes.append('single')

        elif self['flags']['is_index']:
            classes.append('index')

            if self['flags']['is_dir_index']:
                classes.append('dir-index')
            elif self['flags']['is_tag_index']:
                classes.append('tag-index')

        if self['flags']['is_homepage']:
            classes.append('homepage')

        self['classes'] = ' '.join(classes)

    def _set_template(self):
        """ Determines the best-match template for the page. """

        templates = site.templates()
        typeid = self['type']['id']

        # Single-record page.
        if self['flags']['is_single']:
            if self['record'].get('template') in templates:
                template = self['record'].get('template')
            elif 'record-' + typeid in templates:
                template = 'record-' + typeid
            else:
                template = 'record'

        # Tag index page.
        elif self['flags']['is_tag_index']:
            if 'tag-index-' + typeid in templates:
                template = 'tag-index-' + typeid
            elif 'tag-index' in templates:
                template = 'tag-index'
            else:
                template = 'index'

        # Directory index page.
        else:
            if 'dir-index-' + typeid in templates:
                template = 'dir-index' + typeid
            elif 'dir-index' in templates:
                template = 'dir-index'
            else:
                template = 'index'

        self['template'] = template + '.html'


class RecordPage(Page):

    """ Represents a single record. """

    def __init__(self, record):
        Page.__init__(self, record['type'])
        self['record'] = record
        self['slugs'] = record['path']
        self['flags']['is_single'] = True
        self['flags']['is_homepage'] = (record['path'] == ['index'])


class IndexPage(Page):

    """ Represents a (possibly-paged) index of records. """

    def __init__(self, type, slugs, index, per_page):
        Page.__init__(self, type)
        self['slugs'] = slugs
        self['flags']['is_index'] = True

        index.sort(
            key = lambda record: record[self['type']['order_by']],
            reverse = self['type']['reverse']
        )
        self.index = index

        self.per_page = per_page or len(index)
        self.total_pages = math.ceil(float(len(index)) / self.per_page)

    def render(self):
        for page in range(1, self.total_pages + 1):
            self['records'] = self.index[
                self.per_page * (page - 1)
                :
                self.per_page * page
            ]

            if page == 1:
                self['slugs'].append('index')
            else:
                self['slugs'][-1] = 'page-%s' % page

            self['flags']['is_homepage'] = (self['slugs'] == ['index'])
            self._paging(self['slugs'][:-1], page, self.total_pages)

            Page.render(self)

    def _paging(self, slugs, page, total):
        self['paging']['is_paged'] = (total > 1)
        self['paging']['page'] = page
        self['paging']['total'] = total
        self['paging']['prev_url'] = site.paged_url(slugs, page - 1, total)
        self['paging']['next_url'] = site.paged_url(slugs, page + 1, total)
        self['paging']['first_url'] = site.paged_url(slugs, 1, total)
        self['paging']['last_url'] = site.paged_url(slugs, total, total)
