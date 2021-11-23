import logging
import os
import fnmatch
import tqdm
from .build import Build
from .config import Config
from .exceptions import BuildException
from .helpers import import_by_name, remove_directory_contents


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

        # Prefixed files are not added to the initial build list.
        'ignore_prefix': '_',
    }

    def __init__(self, source_directory, output_directory,
                 config_file='_config.json',
                 progress=False):
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.test_directories()

        self.progress = progress

        # Path to the config file. This file will be loaded from the source
        # directory.
        self.config_file = config_file

        # Config dictionary.
        self.config = self.get_config()

        # List of callables which are passed a file path and return True if that
        # path should be ignored.
        self.ignored = []

        self.module_cache = {}

        self.init_ignored()

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
        """Returns a Config object. The config object is filled with the default
        config values and then updated with the values from the config file
        located in the source directory.
        """
        config = self.config_class(self.default_config)
        try:
            config_path = os.path.join(self.source_directory, self.config_file)
            config.from_json_file(config_path)
        except FileNotFoundError:
            logger.warning('Project does not contain the config file.')
        return config

    def init_ignored(self):
        """Adds callables used to detect files which should be ignored and not
        added to the initial build list.
        """
        # Ignore the config file.
        def ignore_config(path):
            if os.path.commonprefix([self.config_file, path]):
                return True
        self.ignored.append(ignore_config)

        # Ignore if any part of the path starts with ignore prefix.
        def ignore_prefixed(path):
            for part in path.split(os.sep):
                if part.startswith(self.config['ignore_prefix']):
                    return True
        self.ignored.append(ignore_prefixed)

    def load_module(self, module_name):
        """Loads a single module.

        module_name: a name of the module.
        """
        try:
            import_name = 'basilisk.modules.' + module_name
            module_class = import_by_name(import_name)
        except:
            # TODO: try load an external module.
            raise
        return module_class(self)

    def get_module(self, module_name):
        """Retrieves a single module from cache or loads it.

        module_name: a name of the module.
        """
        if not module_name in self.module_cache:
            module = self.load_module(module_name)
            self.module_cache[module_name] = module
        return self.module_cache[module_name]

    def get_pipeline(self, build):
        for pipeline in self.config['pipelines']:
            if not 'patterns' in pipeline:
                raise ValueError('missing property: patterns')
            for pattern in pipeline['patterns']:
                if fnmatch.fnmatch(build.input_path, pattern):
                    return pipeline
        return None

    def iter_modules(self, module_names):
        return iter([self.get_module(name) for name in module_names])

    def iter_global_modules(self):
        """Iterates over global modules defined in the config."""
        return self.iter_modules(self.config['modules'])

    def iter_build_modules(self, build):
        """Iterates over build specific modules."""
        pipeline = self.get_pipeline(build)
        return self.iter_modules(pipeline['modules'])

    def should_build(self, path):
        """Decides if a Build using this path as an input should be created.

        path: Path to the file relative to the source directory root.
        """
        for method in self.ignored:
            if method(path):
                return False
        return True

    def builds_generator(self):
        """Yields initial Build objects. All files in the source directory are
        scanned. For each file a build object is created and the output path is
        set to the relative path in the source directory.
        """
        base_path_length = len(self.source_directory) + 1

        for (dirpath, dirnames, filenames) in os.walk(self.source_directory):
            subdirectory = dirpath[base_path_length:]
            for filename in filenames:
                input_path = os.path.join(subdirectory, filename)
                if not self.should_build(input_path):
                    continue

                output_path = input_path

                build = Build(input_path, output_path)
                logger.debug('Yielding object: %s', build)
                yield build

    def add_build(self, build):
        for module in self.iter_build_modules(build):
            logger.debug('Processing using %s', module)
            module.execute(build)
        self.builds_modified = True
        self.builds.append(build)

    def with_progress_bar(self, iterable):
        return tqdm.tqdm(iterable, disable=not self.progress, leave=False)

    def run(self):
        """This is the main function which should be executed to run a build."""
        self.builds = []
        self.builds_modified = False

        logger.info('Scanning files')
        for build in self.builds_generator():
            self.add_build(build)

        while self.builds_modified:
            logger.info('Processing builds')
            self.builds_modified = False
            for module in self.with_progress_bar(self.iter_global_modules()):
                logger.debug('Processing using %s', module)
                module.process(iter(self.builds))

        logger.info('Building')
        for build in self.with_progress_bar(self.builds):
            logger.debug('Building %s', build)
            build.execute(self.config, self.source_directory, self.output_directory)
