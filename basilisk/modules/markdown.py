import markdown
from . import Module


class MarkdownModule(Module):
    """Runs the content of .md files through markdown converter therefore
    converting them to HTML.

    This module doesn't require any additional configuration.
    """

    priority = -5

    def make_processor(self):
        def processor(content, *args, **kwargs):
            return markdown.markdown(content)
        return processor

    def execute(self, builds):
        for build in builds:
            if build.input_path.endswith('.md'):
                processor = self.make_processor()
                build.processors.append(processor)
