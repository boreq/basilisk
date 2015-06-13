import os
from . import Module
from ..templates import Jinja2Templates


class TemplatesModule(Module):
    """Simply runs .html files through templates and copies them otherwise
    unchanged.
    """

    def make_processor(self, templates, input_path):
        def processor(content, context):
            template_context = {
                'content': content,
            }
            template_context.update(context)
            return templates.render(input_path, template_context)
        return processor

    def execute(self, builds):
        default_templates_dir = '%stemplates' % self.builder.config['ignore_prefix']
        templates_dir = self.builder.config.get('templates_directory', default_templates_dir)
        templates_dir = os.path.join(self.builder.source_directory, templates_dir)
        templates = Jinja2Templates(templates_dir)

        for build in builds:
            processor = self.make_processor(templates, build.input_path)
            build.processors.append(processor)
