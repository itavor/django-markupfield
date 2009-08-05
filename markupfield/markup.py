import settings

from django.utils.html import linebreaks, urlize
from django.utils.functional import curry, wraps

def html(text, **kwargs):
    """
    Returns provided HTML after cleanup/sanitazion.
    """
    return text

def plain(text, **kwargs):
    """
    Converts plain text to HTML, and returns the HTML.
    """
    if kwargs.get('linebreaks', False):
        text = linebreaks(text)
    if kwargs.get('urlize', False):
        text = urlize(text)
    return text

def textile(text, **kwargs):
    """
    Applies Textile conversion to text, and returns the HTML.
    """
    from django.contrib.markup.templatetags.markup import textile
    return textile(text)

def markdown(text, **kwargs):
    """
    Applies Markdown conversion to text, and returns the HTML.
    """
    import markdown
    return markdown.markdown(text, **kwargs)

def restructuredtext(text, **kwargs):
    """
    Applies reStructuredText conversion to text, and returns the
    HTML.
    """
    from docutils import core
    parts = core.publish_parts(source=text,
                               writer_name='html4css1',
                               **kwargs)
    return parts['fragment']

class MarkupRenderer(object):
    """
    Generic markup renderer which can handle multiple text-to-HTML
    conversion systems.
    """
    def __init__(self):
        self._filters = {}

    def register(self, filter_name, filter_func, **kwargs):
        """
        Registers a new filter for use.
        """
        self._filters[filter_name] = curry(filter_func, **kwargs)

    def __call__(self, filter_name, text):
        """
        Converts text to HTML using the named filter.
        """
        if filter_name not in self._filters:
            raise ValueError("'%s' is not a registered markup filter. Registered filters are: %s." % \
                (filter_name, ', '.join(self.list_filters())))
        filter_func = self._filters[filter_name]
        return filter_func(text)

    def list_filters(self):
        """
        Returns list of registered markup filters.
        """
        return self._filters.iterkeys()

renderer = MarkupRenderer()

_blank = {}

# Register formats supported by a vanilla Django install

if 'plain' in settings.TYPES_OPTIONS:
    opts = settings.TYPES_OPTIONS['plain'] or _blank
    renderer.register('plain', plain, **opts)

if 'html' in settings.TYPES_OPTIONS:
    opts = settings.TYPES_OPTIONS['html'] or _blank
    renderer.register('html', html, **opts)

# Add formats which depend on external (possibly unavailable) packages

if 'markdown' in settings.TYPES_OPTIONS:
    try:
        import markdown as ignore
    except ImportError:
        pass
    else:
        opts = settings.TYPES_OPTIONS['markdown'] or _blank
        renderer.register('markdown', markdown, **opts)

if 'textile' in settings.TYPES_OPTIONS:
    try:
        import textile as ignore
    except ImportError:
        pass
    else:
        opts = settings.TYPES_OPTIONS['textile'] or _blank
        renderer.register('textile', textile, **opts)

if 'ReST' in settings.TYPES_OPTIONS:
    try:
        from docutils.core import publish_parts
    except ImportError:
        pass
    else:
        opts = settings.TYPES_OPTIONS['ReST'] or _blank
        renderer.register('ReST', restructuredtext, **opts)
