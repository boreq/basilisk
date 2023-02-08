import htmlmin # type: ignore
from ..module import Module


class MinifyHtmlModule(Module):
    """Runs the content through an HTML minifier.

    Example module definition:

        {
            "name": "minify_html"
        }

    """

    def make_processor(self):
        def processor(content, *args, **kwargs):
            return htmlmin.minify(content.decode()).encode()
        return processor

    def execute(self, build, module_config):
        processor = self.make_processor()
        build.processors.append(processor)
