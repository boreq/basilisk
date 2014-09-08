import os
from . import Module
from ..templates import TemplateRenderException


class HtmlModule(Module):
    """Simply runs .html files through templates and copy them otherwise
    unchanged.
    """

    interested_in_ext = ['.html']

    def interested_in(self, path):
        if os.path.splitext(path)[1] in self.interested_in_ext:
            return True
        return False

    def get_context(self, environment, build):
        """Gets the context which is passed to the renered template."""
        return environment.get_context(build)

    def run(self, environment):
        for build in environment.builds:
            self.logger.debug('Building %s', build)
            context = self.get_context(environment, build)
            content = environment.templates.render(build.input_path, context)
            build.write(environment, content)
