import os
from . import Module
from ..templates import Jinja2Templates


class TemplatesModule(Module):
    """Simply runs .html files through templates and copies them otherwise
    unchanged.
    """

    def get_context(self, environment, build):
        """Gets the context which is passed to the renered template."""
        return environment.get_context(build)

    def make_processor(self, templates, input_path):
        def processor(content, parameters):
            context = {
                'content': content,
                'parameters': parameters
            }
            return templates.render(input_path, context)
        return processor

    def execute(self, builds):
        default_templates_dir = '%stemplates' % self.builder.config['ignore_prefix']
        templates_dir = self.builder.config.get('templates_directory', default_templates_dir)
        templates_dir = os.path.join(self.builder.source_directory, templates_dir)
        templates = Jinja2Templates(templates_dir)

        for build in builds:
            processor = self.make_processor(templates, build.input_path)
            build.processors.append(processor)
