"""
    Main class bulding the static website.
"""


from collections import defaultdict
import markdown
import os
import logging
from .config import Config
from .environment import Environment, Build
from .helpers import replace_ext
from .templates import Jinja2Templates


logger = logging.getLogger('builder')


class Builder(object):
    """Main builder.

    Example structure of the source directory:

        _templates/
            _base.html    # Default template. Content is added as content variable.
            _article.html
        _static/          # Static files.
        _config.json
        directory/
            page.en.md
        2014/
            7/
                13/
                    article.en.md
        page.en.md
        page.pl.md

    source_directory: root directory of the project to build.
    output_directory: output directory.
    """

    templates_class = Jinja2Templates
    config_class = Config

    default_config = {
        'url_prefix': '/',
    }

    def __init__(self, source_directory, output_directory):
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.config = self.init_config()
        self.templates = self.init_templates()
        self.modules = []

    def init_config(self):
        config_path = os.path.join(self.source_directory, '_config.json')
        config = self.config_class(self.default_config)
        config.from_json_file(config_path)
        logger.debug('Config is %s, %s', type(config), str(config))
        return config

    def init_templates(self):
        templates_directory = os.path.join(self.source_directory, '_templates')
        templates = self.templates_class(templates_directory)
        logger.debug('Templates are %s', type(templates))
        return templates

    def iter_modules(self):
        return iter(sorted(self.modules, key=lambda x: x.priority))

    def should_build(self, path):
        """Decides if a Build using this path as an input should be created.

        path: Path to the file relative to the source directory root.
        """
        # Ignore if any part of the path starts with an underscore.
        for part in path.split(os.pathsep):
            if part.startswith('_'):
                return False
    
        # Check if any module wants to preprocess that path.
        for module in self.iter_modules():
            if module.interested_in(path):
                return True
            
        return False

    def builds_generator(self):
        """Yields Build objects."""
        base_path_length = len(self.source_directory) + 1

        for (dirpath, dirnames, filenames) in os.walk(self.source_directory):
            logger.debug('Directory %s: %s, %s', dirpath, dirnames, filenames)
            subdirectory = dirpath[base_path_length:]

            for filename in filenames:
                input_path = os.path.join(subdirectory, filename)
                if not self.should_build(input_path):
                    continue
                ext = os.path.splitext(input_path)[1]
                output_path = replace_ext(input_path, ext, '.html')
                build = Build(input_path, output_path)
                logger.debug('Yielding object: %s', build)
                yield build

    def create_initial_environments(self):
        """Creates a list containing an intial environment."""
        builds = [build for build in self.builds_generator()]
        environment = Environment(self.source_directory, self.output_directory,
                                  config=self.config, builds=builds)
        return [environment]

    def run(self):
        environments = self.create_initial_environments()
        logger.debug('Created initial environments: %s', environments)

        for module in self.iter_modules():
            environments = module.preprocess(environments)

        for module in self.iter_modules():
            for environment in environments:
                module.execute(environment)
