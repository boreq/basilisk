import html
from . import Module


class EscapeModule(Module):
    """Incjects a processor to .md files which runs their content through
    markdown converter therefore converting them to html.
    """

    priority = -10

    def make_processor(self):
        def processor(content, *args, **kwargs):
            return html.escape(content)
        return processor

    def should_not_escape(self, path):
        for ext in self.builder.config.get('dont_escape', []):
            if path.endswith(ext):
                return True
        return False

    def execute(self, builds):
        for build in builds:
            if not self.should_not_escape(build.input_path):
                processor = self.make_processor()
                build.processors.append(processor)
