from markup import renderer

from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

def preview(request, markup_type):
    text = request.POST.get('data', '')
    html = renderer(markup_type, text)
    return render_to_response('markupfield/preview.html',
                              {
                                  'html': html,
                                  'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
                               },
                              context_instance=RequestContext(request))
