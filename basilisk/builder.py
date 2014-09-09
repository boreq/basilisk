"""
    Main class bulding the static website.
"""


from collections import defaultdict
import logging
import markdown
import os
from .config import Config
from .environment import Environment, Build
from .exceptions import BuildException
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
    config_file: path to the config file relative to the source directory.
    """

    # Default class used for templates.
    templates_class = Jinja2Templates

    # Default class used for config.
    config_class = Config

    # Default config values.
    default_config = {
        'modules': ['pretty_urls', 'html'],
        'ignore_prefix': '_',
        'templates_directory': '_templates',
    }

    def __init__(self, source_directory, output_directory,
                 config_file='_config.json'):
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.test_directories()

        # Default filename of the config file. This file will be loaded from the
        # source directory.
        self.config_file = config_file

        # Config dictionary.
        self.config = self.get_config()

        # List of callables which are passed a file path and return True if that
        # path should be ignored.
        self.ignored = []

        # List of loaded modules.
        self.modules = []

        self.init_ignored()
        self.init_modules()

    def test_directories(self):
        """Performs sanity checks on the source and output directories."""
        # Check if the source directory exists.
        if not os.path.isdir(self.source_directory):
            raise BuildException('Source directory does not exist.')

        # Check if the output directory is empty and offer to delete its
        # contents otherwise.
        if os.path.exists(self.output_directory):
            if os.listdir(self.output_directory):
                msg = 'Output directory is not empty.'
                logger.error(msg)
                purge = input('Remove directory contents? y/N ')
                if purge.lower() in ['y', 'yes']:
                    remove_directory_contents(self.output_directory)
                else:
                    raise BuildException(msg)

    def get_config(self):
        """Returns Config object."""
        config_path = os.path.join(self.source_directory, self.config_file)
        config = self.config_class(self.default_config)
        try:
            config.from_json_file(config_path)
        except FileNotFoundError:
            logger.warning('Project does not contain the config file.')
        return config

    def init_modules(self):
        """Initializes all modules defined in the config."""
        for module_name in self.config['modules']:
            try:
                import_name = 'basilisk.modules.' + module_name
                module_class = import_by_name(import_name)
            except:
                # TODO: try load an external module.
                raise
            self.load_module(module_class())

    def init_ignored(self):
        """Adds callables used to detect files which should be ignored and not
        added to the initial environment.
        """
        # Ignore templates directory.
        def ignore_templates(path):
            if os.path.commonprefix([self.config['templates_directory'], path]):
                return True

        # Ignore templates directory.
        def ignore_config(path):
            if os.path.commonprefix([self.config_file, path]):
                return True

        # Ignore if any part of the path starts with an underscore.
        def ignore_prefixed(path):
            for part in path.split(os.pathsep):
                if part.startswith('_'):
                    return True

        self.ignored.append(ignore_templates)
        self.ignored.append(ignore_config)
        self.ignored.append(ignore_prefixed)

    def load_module(self, module):
        """Loads a single module.

        module: a class which inherits from Module.
        """
        module.load(self)
        self.modules.append(module)

    def get_templates(self):
        """Returns templates passed to the initial environment."""
        templates_directory = os.path.join(self.source_directory,
                                           self.config['templates_directory'])
        templates = self.templates_class(templates_directory)
        return templates

    def iter_modules(self):
        """Iterates over loaded modules sorted by priority."""
        return iter(sorted(self.modules, key=lambda x: x.priority))

    def should_build(self, path):
        """Decides if a Build using this path as an input should be created.

        path: Path to the file relative to the source directory root.
        """
        for method in self.ignored:
            if method(path):
                return False
        return True

    def builds_generator(self):
        """Yields Build objects used to create initial Environment object."""
        base_path_length = len(self.source_directory) + 1

        for (dirpath, dirnames, filenames) in os.walk(self.source_directory):
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
                                  templates=self.get_templates(),
                                  config=self.config, builds=builds)
        return [environment]

    def run(self):
        environments = self.create_initial_environments()

        for module in self.iter_modules():
            logger.info('Preprocessing with %s', module)
            environments = module.preprocess(environments)

        for module in self.iter_modules():
            logger.info('Running %s', module)
            for environment in environments:
                module. execute(environment)
