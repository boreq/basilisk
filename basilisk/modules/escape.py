import html
from . import Module


class EscapeModule(Module):
    """Escapes all special HTML characters present in the input files. This
    module is useful to escape plaintext files which can contain special
    characters. Remember to exclude file extensions in the config to prevent
    this module from escaping certain files if you want the HTML they contain
    to be rendered.

    Example config:

        {
            "dont_escape": [".html"]
        }

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
