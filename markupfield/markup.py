from django.utils.html import linebreaks, urlize
from django.utils.functional import curry, wraps
from django.utils.translation import ugettext_lazy as _

def html(text, **kwargs):
    """
    Returns provided HTML after cleanup/sanitazion.
    """
    return text

def plain(text, **kwargs):
    """
    Converts plain text to HTML, and returns the HTML.
    """
    return urlize(linebreaks(text))

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

# Include formats supported by a vanilla Django install

DEFAULT_MARKUP_FILTERS = {
    'html': html,
    'plain': plain,
    'textile': textile,
}

class MarkupRenderer(object):
    """
    Generic markup renderer which can handle multiple text-to-HTML
    conversion systems.
    """
    def __init__(self):
        self._filters = {}
        for filter_name, filter_func in DEFAULT_MARKUP_FILTERS.items():
            self.register(filter_name, filter_func)

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
            raise ValueError("'%s' is not a registered markup filter. Registered filters are: %s." % (filter_name,
                                                                                                       ', '.join(self._filters.iterkeys())))
        filter_func = self._filters[filter_name]
        return filter_func(text)

    def list_filters(self):
        """
        Returns list of registered markup filters.
        """
        return self._filters.iterkeys()

renderer = MarkupRenderer()

# Add formats which depend on external (possibly unavailable) packages

try:
    import markdown as ignore
    formatter.register('markdown', markdown)
except ImportError:
    pass

try:
    from docutils.core import publish_parts
    formatter.register('restructuredtext', restructuredtext)
except ImportError:
    pass
