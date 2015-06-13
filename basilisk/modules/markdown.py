import markdown
import os
from . import Module


class MarkdownModule(Module):
    """Converts markdown in .md5 to html."""

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
