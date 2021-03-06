import markdown
from ..module import Module


class MarkdownModule(Module):
    """Runs the content of .md files through markdown converter therefore
    converting them to HTML.

    This module doesn't require any additional configuration.
    """

    def make_processor(self):
        def processor(content, *args, **kwargs):
            return markdown.markdown(content, extensions=['tables'])
        return processor

    def execute(self, build):
        processor = self.make_processor()
        build.processors.append(processor)
