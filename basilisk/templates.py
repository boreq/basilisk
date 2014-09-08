"""
    Template systems.
"""


import os
from .exceptions import TemplateRenderException


class BaseTemplates(object):
    """Base templates. Other templates should inherit from this class.

    Child classes must implement _render_template, not_found_exception and
    initial setup in the constructor.

    template_directory: absolute path to the directory with the template files.
    base_template_name: name of the template which is used if the more specific
                        template does not exis. See _template_name_generator.
    """

    # Exception which rises if the rendered template does not exist.
    not_found_exception = None

    def __init__(self, template_directory, base_template_name='_base.html'):
        self.template_directory = template_directory
        self.base_template_name = base_template_name

    def _template_name_generator(self, path):
        """Returns template names in the following order:

            1. subdirectory/name.html
            2. subdirectory/base_template_name
            3. base_template_name

        path: path of a rendered file relative to the source directory.
        """
        head, tail = os.path.split(path)
        yield os.path.join(head, '%s.html' % tail)
        yield os.path.join(head, self.base_template_name)
        yield self.base_template_name

    def _render_template(self, path, context):
        """This method should render the template with provided context.
        Override this methods to implement new templates.

        path: relative path to the template.
        context: dictionary which should be used as context while rendering
                 the template.
        """
        raise NotImplemented()

    def render(self, path, context):
        """Called during the build to render templates.

        path: path of a rendered file relative to the source directory.
        context: see _render_template.
        """
        for template_path in self._template_name_generator(path):
            try:
                return self._render_template(template_path, context)
            except self.not_found_exception as e:
                pass
        raise TemplateRenderException('Could not render %s. No templates.' % path)


class Jinja2Templates(BaseTemplates):
    """Jinja2 templates."""

    def __init__(self, *args, **kwargs):
        super(Jinja2Templates, self).__init__(*args, **kwargs)
        import jinja2
        loader = jinja2.FileSystemLoader(self.template_directory)
        self.env = jinja2.Environment(loader=loader)
        self.not_found_exception = jinja2.TemplateNotFound

    def _render_template(self, path, context):
        template = self.env.get_template(path)
        return template.render(**context)
