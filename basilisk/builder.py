from collections import defaultdict
import logging
import os
from .build import Build
from .config import Config
from .exceptions import BuildException
from .helpers import replace_ext, import_by_name, remove_directory_contents


logger = logging.getLogger('builder')


class Builder(object):
    """This class loads the config and modules, scans the source directory to
    find the files which should be converted and creates the initial list of
    builds. This list is first passed to all modules for preprocessing and after
    that each build is executed.

    Example usage:

        builder = Builder(source_directory, output_directory)
        builder.run()

    source_directory: root directory of the project to build.
    output_directory: output directory.
    config_file: path to the config file relative to the source directory root.
    """

    # Default class used for config.
    config_class = Config

    # Default config values.
    default_config = {
        # Modules to load.
        'modules': ['pretty_urls', 'html'],
        # Prefixed files are not added to the initial environment's build list.
        'ignore_prefix': '_',
        'just_copy': ['.pdf', '.tar.gz'], 
        'exec': {
            '.py': 'python %s',
            '.sh': 'bash %s'
        }
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
        # Ignore config file.
        def ignore_config(path):
            if os.path.commonprefix([self.config_file, path]):
                return True
        self.ignored.append(ignore_config)

        # Ignore if any part of the path starts with an underscore.
        def ignore_prefixed(path):
            for part in path.split(os.sep):
                if part.startswith(self.config['ignore_prefix']):
                    return True
        self.ignored.append(ignore_prefixed)

    def load_module(self, module):
        """Loads a single module.

        module: a class instance which inherits from Module.
        """
        module.load(self)
        self.modules.append(module)

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

    def should_just_copy(self, path):
        for ext in self.config.get('just_copy', []):
            if path.endswith(ext):
                return True
        return False

    def should_exec_with(self, path):
        for ext, command in self.config.get('exec', {}).items():
            if path.endswith(ext):
                return command
        return None

    def builds_generator(self):
        """Yields Build objects used to create initial Environment object."""
        base_path_length = len(self.source_directory) + 1

        for (dirpath, dirnames, filenames) in os.walk(self.source_directory):
            subdirectory = dirpath[base_path_length:]
            for filename in filenames:
                input_path = os.path.join(subdirectory, filename)
                if not self.should_build(input_path):
                    continue

                just_copy = self.should_just_copy(input_path)
                exec_with = self.should_exec_with(input_path)

                if just_copy:
                    output_path = input_path
                else:
                    ext = os.path.splitext(input_path)[1]
                    output_path = replace_ext(input_path, ext, '.html')

                build = Build(input_path, output_path)
                build.parameters = build.read(self.source_directory)[1] if not just_copy else None
                build.just_copy = just_copy
                build.exec_with = exec_with
                logger.debug('Yielding object: %s', build)
                yield build

    def run(self):
        logger.info('Scanning files')
        builds = [build for build in self.builds_generator()]

        logger.info('Running modules')
        for module in self.iter_modules():
            logger.debug('Running %s', module)
            module.execute(builds)

        logger.info('Building')
        for build in builds:
            logger.debug('Building %s', build)
            build.execute(self.config, self.source_directory, self.output_directory)
