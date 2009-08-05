==================
django-markupfield
==================

An implementation of a custom MarkupField for Django, coupled with a rich
editing widget.  A MarkupField is in essence a TextField with an associated
markup type.  The field also caches its rendered value on the assumption that
disk space is cheaper than CPU cycles in a web application.

This project is based on the work of
`jamesturk <http://github.com/jamesturk/django-markupfield>`_, adding the rich
editing widget and a flexible, extensible markup rendering system.

Installation
============

1. Check out the `latest source <http://github.com/itavor/django-markupfield>`_

2. Ensure the `markupfield` directory is in your python path

3. Add ``'markupfield'`` to your ``INSTALLED_APPS``

4. Add markupfield.urls to your project's urls::

    urlpatterns = patterns('',
        url(r'^markup/', include('markupfield.urls')),
        ...
    )

5. Copy of symlink django-markupfield/markupfield/media/markupfield to your
   Django admin media directory::
   
    ln -s <path_to_app>/django-markupfield/markupfield/media/markupfield <path_to_django>/django/contrib/admin/media/

Settings
========

MARKUP_USE_MARKITUP:
    If set to True or not defined, MarkupField editing forms will use the `MarkItUp!`
    rich editing widget. The widget will update itself for the currently selected
    markup type.

MARKUP_TYPES_OPTIONS:
    A dictionary defining markup types which will be available for use, along with
    optional parameters to be passed to each markup rendrering function.

    Omitting this setting is equivalent to setting::

        MARKUP_TYPES_OPTIONS = {
            'plain': {'urlize': True, 'linebreaks': True},
            'html': None,
            'markdown': None,
            'textile': {'encoding': 'utf-8', 'output': 'utf-8'},
            'ReST': None,
        }

    The actual markup types available will be limited to those for which a renderer
    is available. The requirements for the default renderers are:

        html:
            Always available
        plain:
            Always available
        markdown:
            `python-markdown`_
        restructuredtext:
            `docutils`_
        textile:
            `textile`_

Custom Markup Types
-------------------

Additional markup types can be defined by writing a rendering function and registering
it with the app::

    import imaginary_markup_library
    from markupfield.markup import renderer

    def render_imaginary_markup(markup, **kwargs):
        return imaginary_markup_library.render(markup, **kwargs)

    renderer.register('imaginary', render_imaginary_markup, option1='yes', option2='no')

.. _`markdown`: http://daringfireball.net/projects/markdown/
.. _`ReST`: http://docutils.sourceforge.net/rst.html
.. _`textile`: http://hobix.com/textile/quick.html
.. _`python-markdown`: http://www.freewisdom.org/projects/python-markdown/
.. _`docutils`: http://docutils.sourceforge.net/
.. _`python-textile`: http://pypi.python.org/pypi/textile

Usage
=====

Using MarkupField is relatively easy, it can be used in any model definition::

    from django.db import models
    from markupfield.fields import MarkupField

    class Article(models.Model):
        title = models.CharField(max_length=100)
        slug = models.SlugField(max_length=100)
        body = MarkupField()

``Article`` objects can then be created with any markup type defined in 
``MARKUP_FIELD_TYPES``::

    Article.objects.create(title='some article', slug='some-article',
                           body='*fancy*', body_markup_type='markdown')

You will notice that a field named ``body_markup_type`` exists that you did
not declare, MarkupField actually creates two extra fields here 
``body_markup_type`` and ``_body_rendered``.  These fields are always named
according to the name of the declared ``MarkupField``.

Arguments
---------

``MarkupField`` also takes two optional arguments ``default_markup_type`` and
``markup_type``.  Either of these arguments may be specified but not both.

``default_markup_type``:
    Set a markup_type that the field will default to if one is not specified.
    It is still possible to edit the markup type attribute and it will appear
    by default in ModelForms.

``markup_type``:
    Set markup type that the field will always use, ``editable=False`` is set
    on the hidden field so it is not shown in ModelForms.

Accessing a MarkupField on a model
----------------------------------

When accessing an attribute of a model that was declared as a ``MarkupField``
a special ``Markup`` object is returned.  The ``Markup`` object has three
parameters:

``raw``:
    The unrendered markup.
``markup_type``:
    The markup type.
``rendered``:
    The rendered HTML version of ``raw``, this attribute is read-only.

This object has a ``__unicode__`` method that calls 
``django.utils.safestring.mark_safe`` on ``rendered`` allowing MarkupField
objects to appear in templates as their rendered selfs without any template
tag or having to access ``rendered`` directly.

Assuming the ``Article`` model above::

    >>> a = Article.objects.all()[0]
    >>> a.body.raw
    u'*fancy*'
    >>> a.body.markup_type
    u'markdown'
    >>> a.body.rendered
    u'<p><em>fancy</em></p>'
    >>> print unicode(a.body)
    <p><em>fancy</em></p>

Assignment to ``a.body`` is equivalent to assignment to ``a.body.raw`` and
assignment to ``a.body_markup_type`` is equivalent to assignment to 
``a.body.markup_type``.

.. note::
    a.body.rendered is only updated when a.save() is called


Todo
====

 * add unit tests for new features
 * explore possibility of merging with jamesturk's trunk

Origin
======

For those coming here via django snippets or the tracker, my original implementation is at https://gist.github.com/67724/3b7497713897fa0021d58e46380e4d80626b6da2

Jacob Kaplan-Moss commented on twitter that he'd possibly like to see a MarkupField in core and I filed a ticket on the Django trac http://code.djangoproject.com/ticket/10317

The resulting django-dev discussion drastically changed the purpose of the field.  While I initially intended to write a version that seemed more acceptable for Django core I wound up feeling that the 'acceptable' version had so little functionality and so much complexity it wasn't worth using.

