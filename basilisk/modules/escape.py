import html
from ..module import Module


class EscapeModule(Module):
    """Escapes all special HTML characters present in the input files. This
    module is useful to escape plaintext files which can contain special
    characters. 

    Example module definition:

        {
            "name": "escape"
        }

    """

    def make_processor(self):
        def processor(content, *args, **kwargs):
            return html.escape(content.decode()).encode()
        return processor

    def execute(self, build, module_config):
        processor = self.make_processor()
        build.processors.append(processor)
