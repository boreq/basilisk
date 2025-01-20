import os
import io
import subprocess
from ..module import Module
from PIL import Image


class ResizeModule(Module):
    """Resize resizes images and videos.

    Example module definition:

        {
            "name": "resize"
            "config": {
                "max_width": 1000,
                "max_height": 1000
            }
        }

    Define at least one of the following keys: `max_width` or `max_height`.
    """

    def make_processor(self, build, module_config):
        ext = os.path.splitext(build.output_path)[1].lower()

        if ext in ['.jpg', '.jpeg', '.png']:
            return ImageResizerProcessorBuilder.make_processor(self, build, module_config)

        if ext in ['.webm']:
            return VideoResizerProcessorBuilder.make_processor(self, build, module_config)

        raise Exception('resize module doesn\'t support files with extension \'{}\''.format(ext))

    def execute(self, build, module_config):
        processor = self.make_processor(build, module_config)
        build.processors.append(processor)


class ImageResizerProcessorBuilder:

    @staticmethod
    def _get_format(build):
        extensions = Image.registered_extensions()
        ext = os.path.splitext(build.output_path)[1].lower()
        return extensions[ext]

    @staticmethod
    def _get_target_size(module, module_config, image):
        width, height = image.size

        max_width = module.config_get(module_config, 'max_width', None)
        if max_width is not None:
            if width > max_width:
                ratio = width / max_width
                height = int(height / ratio)
                width = max_width

        max_height = module.config_get(module_config, 'max_height', None)
        if max_height is not None:
            if height > max_height:
                ratio = height / max_height
                width = int(width / ratio)
                height = max_height

        return width, height

    @staticmethod
    def make_processor(module, build, module_config):
        def processor(content, *args, **kwargs):
            fmt = ImageResizerProcessorBuilder._get_format(build)
            with io.BytesIO(content) as inpt:
                with Image.open(inpt) as image:
                    target_size = ImageResizerProcessorBuilder._get_target_size(module, module_config, image)
                    resized_image = image.resize(target_size, Image.LANCZOS)
                    with io.BytesIO() as output:
                        kwargs = {}
                        if image.info.get('exif', None) is not None:
                            kwargs['exif'] = image.info['exif']
                        resized_image.save(output, fmt, **kwargs)
                        return output.getvalue()
        return processor


class VideoResizerProcessorBuilder:

    @staticmethod
    def _get_size(module_config, content):
        result = subprocess.run(
            [
                'ffprobe',
                '-v',
                'error',
                '-select_streams',
                'v:0',
                '-show_entries',
                'stream=width,height',
                '-of',
                'csv=s=x:p=0', 
                '-i', 
                '-', 
            ],
            input=content,
            capture_output=True,
        )

        if result.returncode != 0:
            raise Exception('ffprobe error: {}'.format(result.stderr))

        trimmed_stdout = result.stdout.strip()
        split_stdout = trimmed_stdout.split(b'x')
        if len(split_stdout) != 2:
            raise Exception('unexpected stdout format \'{}\''.format(result.stdout))

        return int(split_stdout[0]), int(split_stdout[1])

    @staticmethod
    def _get_target_size(module, module_config, input_width, input_height):
        target_width, target_height = input_width, input_height

        max_width = module.config_get(module_config, 'max_width', None)
        if max_width is not None:
            if input_width > max_width:
                ratio = input_width / max_width
                target_height = int(input_height / ratio)
                target_width = max_width

        max_height = module.config_get(module_config, 'max_height', None)
        if max_height is not None:
            if input_height > max_height:
                ratio = input_height / max_height
                target_height = max_height
                target_width = int(input_width / ratio)

        return target_width, target_height

    @staticmethod
    def _resize(build, content, target_width, target_height):
        ext = os.path.splitext(build.input_path)[1].lower()
        ext = ext.lstrip('.')

        result = subprocess.run(
            [
                'ffmpeg',
                '-f',
                ext,
                '-i',
                'pipe:',
                '-filter:v',
                'scale={}:{}'.format(target_width, target_height),
                '-f',
                ext,
                'pipe:',
            ],
            input=content,
            capture_output=True,
        )

        if result.returncode != 0:
            raise Exception('ffmpeg error: {}'.format(result.stderr))

        return result.stdout

    @staticmethod
    def make_processor(module, build, module_config):
        def processor(content, *args, **kwargs):
            input_width, input_height = VideoResizerProcessorBuilder._get_size(module_config, content)
            target_width, target_height = VideoResizerProcessorBuilder._get_target_size(module, module_config, input_width, input_height)
            return VideoResizerProcessorBuilder._resize(build, content, target_width, target_height)

        return processor
