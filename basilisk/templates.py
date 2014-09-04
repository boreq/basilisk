"""
    Template systems.
"""


import logging
import os


logger = logging.getLogger('templates')


class TemplateRenderException(Exception):
    pass


class BaseTemplates(object):
    """Base templates. Other templates should inherit fromt his class.

    template_directory: absolute path to the directory with the template files.
    base_template_name: name of the template which is used if the more specific
                        template does not exis. See _template_name_generator.
    """

    template_not_found_exception = None

    def __init__(self, template_directory, base_template_name='_base.html'):
        self.template_directory = template_directory
        self.base_template_name = base_template_name

    def _template_name_generator(self, subdirectory, name):
        """Returns template names in the following order:

            1. subdirectory/name.html
            2. subdirectory/base_template_name
            3. base_template_name

        subdirectory: template subdirectory.
        name: template name.
        """
        yield os.path.join(subdirectory, '%s.html' % name)
        yield os.path.join(subdirectory, self.base_template_name)
        yield self.base_template_name

    def _render_template(self, path, context):
        """This method should render the template with provided context.

        path: relative path to the template.
        context: dictionary which should be used as context while rendering 
                 the template.
        """
        raise NotImplemented()

    def render(self, subdirectory, name, context):
        """Called during the build to render templates.

        subdirectory: see _template_name_generator.
        name: see _template_name_generator.
        context: see _render_template.
        """
        for path in self._template_name_generator(subdirectory, name):
            try:
                return self._render_template(path, context)
            except self.template_not_found_exception as e:
                logger.debug('Could not render %s', path)
        raise TemplateRenderException('Could not render %s', name)


class Jinja2Templates(BaseTemplates):
    """Class rendering Jinja2 templates."""

    def __init__(self, template_directory):
        super(Jinja2Templates, self).__init__(template_directory)
        import jinja2
        loader = jinja2.FileSystemLoader(self.template_directory)
        self.env = jinja2.Environment(loader=loader)
        self.template_not_found_exception = jinja2.TemplateNotFound

    def _render_template(self, path, context):
        template = self.env.get_template(path)
        return template.render(**context)
