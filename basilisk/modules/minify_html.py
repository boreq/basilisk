import htmlmin
from ..module import Module


class MinifyHtmlModule(Module):
    """Runs the content through an HTML minifier.

    This module doesn't require any additional configuration.
    """

    def make_processor(self):
        def processor(content, *args, **kwargs):
            return htmlmin.minify(content)
        return processor

    def execute(self, build):
        processor = self.make_processor()
        build.processors.append(processor)
