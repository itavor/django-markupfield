from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminTextareaWidget

class MarkupTextarea(forms.widgets.Textarea):
    """
    A markup-enabled Textarea widget.
    """
    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, unicode):
            value = value.raw
        return super(MarkupTextarea, self).render(name, value, attrs)

_media_prefix = settings.ADMIN_MEDIA_PREFIX + 'markupfield/'

_markup_js = u"""
<script type="text/javascript">
    var _markup_media_prefix = "%(prefix)s";
    jQuery(document).ready(function () {
        DJMARKUP.init_field("%(name)s");
    });
</script>
"""

class RichMarkupTextarea(MarkupTextarea):
    """
    A MarkupTextarea widget with a rich editing UI, using MarkItUp!.
    """
    class Media:
        css = {
            'all': (_media_prefix + 'markupfield.css',
                    _media_prefix + 'markitup/skins/admin/style.css'),
        }
        js = (
            _media_prefix + 'jquery.pack.js',
            _media_prefix + 'jquery.markitup.pack.js',
            _media_prefix + 'markupfield.js',
        )

    def render(self, name, value, attrs=None):
        output = [super(RichMarkupTextarea, self).render(name, value, attrs)]
        output.append(_markup_js % {'name': name, 'prefix': _media_prefix})
        return mark_safe(u''.join(output))

class AdminMarkupTextareaWidget(MarkupTextarea, AdminTextareaWidget):
    """
    A MarkupTextarea widget with (optional, currently non-existent)
    admin-specific styling.
    """
    pass


class AdminRichMarkupTextareaWidget(RichMarkupTextarea):
    """
    A MarkupTextarea widget with a rich editing interface.
    """
    pass
