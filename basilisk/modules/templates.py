import os
from ..module import Module
from ..templates import Jinja2Templates


class TemplatesModule(Module):
    """Runs all files through templates. The templates should be present in the
    templates directory which is specified in the config file. The path to the
    template directory is a path relative to the source directory root. The
    template system will try to match the name of the template file to the name
    of the output file in the following manner:

        1. The exact name of the file with the extension changed to ".html".
        2. A file called "_base.html" located in the same directory.
        3. A file called "_base.html" located in any of the parent directories.

    For example for the file "dir1/dir2/index.html" the module would attempt to
    load the following templates:

        1. dir1/dir2/index.html
        2. dir1/dir2/_base.html
        3. dir1/_base.html
        4. _base.html

    Example config:

        {
            "templates_directory": "_templates"
        }

    """

    config_key = 'templates'

    def make_processor(self, templates, input_path):
        def processor(content, context):
            template_context = {
                'content': content.decode(),
            }
            template_context.update(context)
            return templates.render(input_path, template_context).encode()
        return processor
    
    def get_templates_dir(self):
        default_templates_dir = '%stemplates' % self.builder.config['ignore_prefix']
        templates_dir = self.config_get('templates_directory', default_templates_dir)
        return os.path.join(self.builder.source_directory, templates_dir)

    def get_templates(self):
        if not hasattr(self, 'templates'):
            templates_dir = self.get_templates_dir()
            self.templates = Jinja2Templates(templates_dir)
        return self.templates

    def execute(self, build):
        templates = self.get_templates()
        processor = self.make_processor(templates, build.input_path)
        build.processors.append(processor)
