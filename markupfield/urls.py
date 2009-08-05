from django.conf.urls.defaults import *

urlpatterns = patterns('markupfield.views',
    url(r'preview/(?P<markup_type>.*)/$', 'preview'),
)
