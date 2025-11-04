from ..module import Module
from ..helpers import replace_last_ext


class ChangeExtensionModule(Module):
    """Changes the extension of the file.

    Example module definition:

        {
            "name": "change_extension",
            "config": {
                "to": "html"
            }
        }

    """

    def execute(self, build, module_config):
        extension = self.config_get(module_config, 'to', None)
        if extension is None:
            raise ValueError('no extension to which to change provided')
        build.output_path = replace_last_ext(build.output_path, '.' + extension)
