import html
from ..module import Module


class EscapeModule(Module):
    """Escapes all special HTML characters present in the input files. This
    module is useful to escape plaintext files which can contain special
    characters. 

    This module doesn't require any additional configuration.
    """

    def make_processor(self):
        def processor(content, *args, **kwargs):
            return html.escape(content)
        return processor

    def execute(self, build):
        processor = self.make_processor()
        build.processors.append(processor)
