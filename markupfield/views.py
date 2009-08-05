from markup import renderer

from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

def preview(request, markup_type):
    """
    Display posted text, rendered in HTML using specified markup.
    """
    text = request.POST.get('data', '')
    html = renderer(markup_type, text)
    ctx = RequestContext(request, {
        'html': html,
        'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
    })
    return render_to_response('markupfield/preview.html', ctx)
