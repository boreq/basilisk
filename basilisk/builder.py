"""
    Main class bulding the static website.
"""


from collections import defaultdict
import logging
import markdown
import os
from .config import Config
from .environment import Environment, Build
from .helpers import replace_ext, import_by_name, remove_directory_contents
from .templates import Jinja2Templates


logger = logging.getLogger('builder')


class Builder(object):
    """Main class which coordinates everything.

    Usage:

        builder = Builder(source_directory, output_directory)
        builder.run()

    source_directory: root directory of the project to build.
    output_directory: output directory.
    """

    templates_class = Jinja2Templates
    config_class = Config

    default_config = {
        'url_prefix': '/',
        'modules': ['html'],
    }

    def __init__(self, source_directory, output_directory):
        self.source_directory = source_directory
        self.output_directory = output_directory

        if not os.path.isdir(source_directory):
            msg = 'Source directory does not exist.'
            logger.critical(msg)
            raise ValueError(msg)

        if os.path.exists(output_directory):
            logger.warning('Output directory already exists.')
            if os.listdir(output_directory):
                msg = 'Output directory is not empty.'
                logger.error(msg)
                purge = input('Remove directory contents? y/N ')
                if purge.lower() in ['y', 'yes']:
                    remove_directory_contents(output_directory)
                else:
                    raise ValueError(msg)

        self.config = self.init_config()
        self.templates = self.init_templates()
        self.modules = self.init_modules()

    def init_config(self):
        config_path = os.path.join(self.source_directory, '_config.json')
        config = self.config_class(self.default_config)
        try:
            config.from_json_file(config_path)
        except FileNotFoundError:
            logger.warning('Project does not contain _config.py file')
        logger.debug('Config is %s, %s', type(config), str(config))
        return config

    def init_templates(self):
        templates_directory = os.path.join(self.source_directory, '_templates')
        templates = self.templates_class(templates_directory)
        logger.debug('Templates are %s', type(templates))
        return templates

    def init_modules(self):
        modules = []
        for module_name in self.config['modules']:
            try:
                import_name = 'basilisk.modules.' + module_name
                module_class = import_by_name(import_name)
            except:
                raise
            module = module_class(self.config)
            modules.append(module)
        return modules

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
                                  self.templates, config=self.config,
                                  builds=builds)
        return [environment]

    def run(self):
        environments = self.create_initial_environments()
        logger.debug('Created initial environments: %s', environments)

        for module in self.iter_modules():
            logger.info('Preprocessing with %s', module)
            environments = module.preprocess(environments)

        for module in self.iter_modules():
            logger.info('Running %s', module)
            for environment in environments:
                module.run(environment)
