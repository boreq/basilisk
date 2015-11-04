import markdown
from . import Module


class MarkdownModule(Module):
    """Injects a processor to .md files which runs their content through
    markdown converter therefore converting them to html.
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
