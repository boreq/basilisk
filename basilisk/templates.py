import os
from .exceptions import TemplateRenderException
from .helpers import replace_ext


class BaseTemplates(object):
    """Base templates. Other templates should inherit from this class. Child
    classes must implement _render_template and initial setup in the
    constructor.

    template_directory: absolute path to the directory with the template files.
    base_template_name: name of the template which is used if the more specific
                        template does not exis. See _template_name_generator.
                        It might be a good idea to prefix this name with
                        a rarely used character in order to avoid conflicts
                        with templates for specific pages.
    """

    def __init__(self, template_directory, base_template_name='_base.html'):
        self.template_directory = template_directory
        self.base_template_name = base_template_name

    def _template_name_generator(self, path):
        """For the path `subdirectory/name.ext` and base template name
        `_base.html` this function would return template names in the following
        order:

            1. subdirectory/name.html
            2. subdirectory/_base.html
            3. _base.html

        path: path of a rendered file relative to the source directory.
        """
        head, tail = os.path.split(path)
        base, ext = os.path.splitext(tail)
        yield replace_ext(path, ext, '.html')

        while True:
            yield os.path.join(head, self.base_template_name)
            head, tail = os.path.split(head)
            if not head:
                break

        yield self.base_template_name

    def _render_template(self, path, context):
        """This method should render the template with provided context.
        Override this methods to implement new templates.

        path: relative path to the template.
        context: dictionary which should be used as context while rendering
                 the template.
        """
        raise NotImplementedError

    def list_templates(self):
        """This method returns a list of paths to all templates that may be
        used during rendering.
        """
        raise NotImplementedError

    def render(self, path, context):
        """Called during the build to render templates.

        path: path of a source file relative to the source directory.
        context: see _render_template.
        """
        for template_path in self._template_name_generator(path):
            if template_path in self.env.list_templates():
                return self._render_template(template_path, context)
        raise TemplateRenderException('Could not render %s. No templates.' % path)


class Jinja2Templates(BaseTemplates):
    """Jinja2 templates."""

    def __init__(self, *args, **kwargs):
        extensions = kwargs.pop('extensions', [])
        super(Jinja2Templates, self).__init__(*args, **kwargs)
        import jinja2
        loader = jinja2.FileSystemLoader(self.template_directory)
        self.env = jinja2.Environment(loader=loader, extensions=extensions)

    def list_templates(self):
        return [os.path.join(self.template_directory, path) for path in self.env.list_templates()]

    def _render_template(self, path, context):
        template = self.env.get_template(path)
        return template.render(**context)


class InternationalizedJinja2Templates(Jinja2Templates):
    """Jinja2 templates with i18n support."""

    def __init__(self, *args, **kwargs):
        self.locale = kwargs.pop('locale')
        self.translations_directory = kwargs.pop('translations_directory')
        self._locale = None
        self._translations = None
        kwargs.setdefault('extensions', [])
        kwargs['extensions'].append('jinja2.ext.i18n')
        super(InternationalizedJinja2Templates, self).__init__(*args, **kwargs)
        self.env.install_gettext_callables(
             lambda x: self.get_translations().ugettext(x),
             lambda s, p, n: self.get_translations().ungettext(s, p, n),
             newstyle=True
         )

    def get_translations(self):
        if not self._translations:
            from babel.support import Translations
            self._translations = Translations.load(self.translations_directory,
                                                   self.get_locale())
        return self._translations

    def get_locale(self):
        if not self._locale:
            from babel.core import Locale
            self._locale = Locale.parse(self.locale)
        return self._locale
