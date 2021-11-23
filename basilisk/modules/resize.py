import os
import io
from ..module import Module
from PIL import Image


class ResizeModule(Module):
    """Resize resizes images.

    Example module definition:

        {
            "name": "copy"
            "config": {
                "max_width": 1000,
                "max_height": 1000
            }
        }

    Define at least one of the following keys: `max_width` or `max_height`.
    """

    def get_format(self, build):
        extensions = Image.registered_extensions()
        ext = os.path.splitext(build.output_path)[1].lower()
        return extensions[ext]

    def get_target_size(self, module_config, image):
        width, height = image.size

        max_width = self.config_get(module_config, 'max_width', None)
        if max_width is not None:
            if width > max_width:
                ratio = width / max_width
                height = int(height / ratio)
                width = max_width

        max_height = self.config_get(module_config, 'max_height', None)
        if max_height is not None:
            if height > max_height:
                ratio = height / max_height
                width = int(width / ratio)
                height = max_height

        return width, height

    def make_processor(self, build, module_config):
        def processor(content, *args, **kwargs):
            fmt = self.get_format(build)
            with io.BytesIO(content) as inpt:
                with Image.open(inpt) as image:
                    target_size = self.get_target_size(module_config, image)
                    resized_image = image.resize(target_size, Image.LANCZOS)
                    with io.BytesIO() as output:
                        resized_image.save(output, fmt, exif=image.info['exif'])
                        return output.getvalue()
        return processor

    def execute(self, build, module_config):
        processor = self.make_processor(build, module_config)
        build.processors.append(processor)
