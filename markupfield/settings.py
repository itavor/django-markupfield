from django.conf import settings

USE_MARKITUP = getattr(settings, 'MARKUP_USE_MARKITUP', True)

TYPES_OPTIONS = getattr(settings, 'MARKUP_TYPES_OPTIONS', None)
if TYPES_OPTIONS is None:
    TYPES_OPTIONS = {
        'plain': {'urlize': True, 'linebreaks': True},
        'html': None,
        'markdown': None,
        'textile': {'encoding': 'utf-8', 'output': 'utf-8'},
        'ReST': None,
    }
