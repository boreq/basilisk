import os
import io
import subprocess
import tempfile
import pathlib
from ..module import Module


class ConvertModule(Module):
    """Conver convers images and videos.

    Example module definition:

        {
            "name": "convert"
            "config": {
                "to": "webp",
            }
        }

    The following key is required: `webp`.
    """

    def make_processor(self, build, module_config):
        to = self.config_get(module_config, 'to', None)

        if to in ['webp']:
            return WebpProcessorBuilder.make_processor(self, build, module_config)

        raise Exception('convert module doesn\'t support converting to \'{}\''.format(to))

    def execute(self, build, module_config):
        processor = self.make_processor(build, module_config)
        build.processors.append(processor)


class WebpProcessorBuilder:

    @staticmethod
    def make_processor(module, build, module_config):
        def processor(content, *args, **kwargs):
            output_path = pathlib.Path(build.output_path)
            build.output_path = os.path.join(output_path.parent, '{}.webp'.format(output_path.stem))

            with tempfile.TemporaryDirectory() as directory:
                path_in = os.path.join(directory, 'input_file')
                path_out = os.path.join(directory, 'output_file.webp')

                with open(path_in, 'wb') as f:
                    f.write(content)

                result = subprocess.run(
                    [
                        'cwebp',
                        '-q',
                        '90',
                        path_in,
                        '-o',
                        path_out,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                with open(path_out, 'rb') as f:
                    content = f.read()

                return content

        return processor
