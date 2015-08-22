
""" Adds a syntax-highlighting filter to Ibis templates. """

import html
import ibis


try:
    import pygments
    import pygments.lexers
    import pygments.formatters
except ImportError:
    pygments = None


@ibis.filters.register('pygmentize')
def pygmentize(text, lang=None):
    if pygments:
        if lang:
            try:
                lexer = pygments.lexers.get_lexer_by_name(lang)
            except pygments.util.ClassNotFound:
                lexer = None
        else:
            try:
                lexer = pygments.lexers.guess_lexer(text)
            except pygments.util.ClassNotFound:
                lexer = None
        if lexer:
            formatter = pygments.formatters.HtmlFormatter(nowrap=True)
            text = pygments.highlight(text, lexer, formatter)
        else:
            text = html.escape(text)
    else:
        text = html.escape(text)
    return text
