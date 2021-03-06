import widgets
import settings
from markup import renderer

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.functional import curry
from django.core.exceptions import ImproperlyConfigured

_rendered_field_name = lambda name: '_%s_rendered' % name
_markup_type_field_name = lambda name: '%s_markup_type' % name

class Markup(object):

    def __init__(self, instance, field_name, rendered_field_name,
                 markup_type_field_name):
        # instead of storing actual values store a reference to the instance
        # along with field names, this makes assignment possible
        self.instance = instance
        self.field_name = field_name
        self.rendered_field_name = rendered_field_name
        self.markup_type_field_name = markup_type_field_name

    # raw is read/write
    def _get_raw(self):
        return self.instance.__dict__[self.field_name]

    def _set_raw(self, val):
        setattr(self.instance, self.field_name, val)

    raw = property(_get_raw, _set_raw)

    # markup_type is read/write
    def _get_markup_type(self):
        return self.instance.__dict__[self.markup_type_field_name]

    def _set_markup_type(self, val):
        return setattr(self.instance, self.markup_type_field_name, val)

    markup_type = property(_get_markup_type, _set_markup_type)

    # rendered is a read only property
    def _get_rendered(self):
        return getattr(self.instance, self.rendered_field_name)
    rendered = property(_get_rendered)

    # allows display via templates to work without safe filter
    def __unicode__(self):
        return mark_safe(self.rendered)


class MarkupDescriptor(object):

    def __init__(self, field):
        self.field = field
        self.rendered_field_name = _rendered_field_name(self.field.name)
        self.markup_type_field_name = _markup_type_field_name(self.field.name)

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError('Can only be accessed via an instance.')
        markup = instance.__dict__[self.field.name]
        if markup is None:
            return None
        return Markup(instance, self.field.name, self.rendered_field_name,
                      self.markup_type_field_name)

    def __set__(self, obj, value):
        if isinstance(value, Markup):
            obj.__dict__[self.field.name] = value.raw
            setattr(obj, self.rendered_field_name, value.rendered)
            setattr(obj, self.markup_type_field_name, value.markup_type)
        else:
            obj.__dict__[self.field.name] = value

class MarkupField(models.TextField):

    def __init__(self, verbose_name=None, name=None, markup_type=None,
                 default_markup_type=None, **kwargs):
        if markup_type and default_markup_type:
            raise ValueError('Cannot specify both markup_type and default_markup_type')
        self.default_markup_type = markup_type or default_markup_type
        markup_types = renderer.list_filters()
        if self.default_markup_type and (not self.default_markup_type in markup_types):
            raise ValueError('Invalid markup type, allowed values: %s' % \
                             ', '.join(renderer.list_filters()))
        self.markup_type_editable = markup_type is None
        super(MarkupField, self).__init__(verbose_name, name, **kwargs)

    def contribute_to_class(self, cls, name):
        keys = renderer.list_filters()
        markup_type_field = models.CharField(max_length=30,
            choices=[(k, k) for k in keys], default=self.default_markup_type,
            editable=self.markup_type_editable, blank=self.blank)
        rendered_field = models.TextField(editable=False)
        markup_type_field.creation_counter = self.creation_counter + 1
        rendered_field.creation_counter = self.creation_counter + 2
        cls.add_to_class(_markup_type_field_name(name), markup_type_field)
        cls.add_to_class(_rendered_field_name(name), rendered_field)
        super(MarkupField, self).contribute_to_class(cls, name)

        setattr(cls, self.name, MarkupDescriptor(self))

    def pre_save(self, model_instance, add):
        value = super(MarkupField, self).pre_save(model_instance, add)
        rendered = renderer(value.markup_type, value.raw)
        setattr(model_instance, _rendered_field_name(self.attname), rendered)
        return value.raw

    def get_db_prep_value(self, value):
        if isinstance(value, Markup):
            return value.raw
        else:
            return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value.raw

    def formfield(self, **kwargs):
        defaults = {'widget': settings.USE_MARKITUP and \
                    widgets.RichMarkupTextarea or widgets.MarkupTextarea}
        defaults.update(kwargs)
        return super(MarkupField, self).formfield(**defaults)

# Register MarkupField to use the custom widget in the Admin
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
FORMFIELD_FOR_DBFIELD_DEFAULTS[MarkupField] = {
    'widget': settings.USE_MARKITUP and \
        widgets.AdminRichMarkupTextareaWidget or \
        widgets.AdminMarkupTextareaWidget
}
