from django.conf import settings

USE_MARKITUP = getattr(settings, 'MARKUP_USE_MARKITUP', True)
