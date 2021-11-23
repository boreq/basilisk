import markdown
from ..module import Module
from ..helpers import replace_last_ext


class MarkdownModule(Module):
    """Runs the content of .md files through markdown converter therefore
    converting them to HTML.

    This module doesn't require any additional configuration.
    """

    def make_processor(self):
        def processor(content, *args, **kwargs):
            return markdown.markdown(content.decode(), extensions=['tables']).encode()
        return processor

    def execute(self, build, module_config):
        processor = self.make_processor()
        build.processors.append(processor)
        build.output_path = replace_last_ext(build.output_path, '.html')
