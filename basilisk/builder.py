"""
    Main class bulding the static website.
"""


from collections import defaultdict
import json
import os
import logging


logger = logging.getLogger('builder')


class Config(dict):
    """A dictionary which provides additional methods to load values from files.

    Keys:
        languages: list of language codes.
                   Example:
                   ["en", "pl"]
    """

    def from_json_file(self, file_path):
        with open(file_path, 'r') as f:
            self.update(json.load(f))


class Build(object):
    """Build.

    directory: relative directory containing that file.
    base_name: base name of the file.
    files: dict with languages as keys and file names as values.
    """

    def __init__(self, subdirectory, base_name, files):
        self.subdirectory = subdirectory
        self.base_name = base_name
        self.files = files

    def run(self, config, source_directory, destination_directory):
        pass


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

    Used names using 'example_path.en.ext' as an example filename:
        base_name: 'example_path'
        root_name: 'example_path.en'
        lang: 'en'
        extension: '.ext'

    source_directory: root directory of the project to build.
    destination_directory: output directory.
    """

    supported_extensions = ['.md', '.html']

    def __init__(self, source_directory, destination_directory):
        self.source_directory = source_directory
        self.destination_directory = destination_directory
        self.load_config()

    def load_config(self):
        self.config = Config()
        self.config.from_json_file(os.path.join(self.source_directory, '_config.json'))
        logger.debug('Config is %s', self.config)

    def split_name(self, root_name):
        """Splits root name into base name and language.

        root_name: filename without the extension.
        """
        root_name = root_name.split('.')
        base_name = ''.join(root_name[:-1])
        lang = root_name[-1]
        return (base_name, lang)

    def should_build(self, path):
        """Decides if the file should be built.

        path: Path to the file relative to the source directory root.
        """
        root_name, extension = os.path.splitext(path)
        if not extension in self.supported_extensions:
            return False
        if path.startswith('_'):
            return False
        return True

    def get_files_to_build(self, subdirectory, filenames):
        """Returns dictionary structured as follows:
        {base_name: {lang: filename, ...}, ...}

        subdirectory: Path to the file directory relative to the source directory root.
        filenames: List of filenames in that directory.
        """
        files_to_build = defaultdict(lambda: {})
        for filename in  filenames:
            path = os.path.join(subdirectory, filename)
            if not self.should_build(path):
                continue
            root_name = os.path.splitext(filename)[0]
            base_name, lang = self.split_name(root_name)
            files_to_build[base_name][lang] = filename
        return files_to_build

    def builds_generator(self):
        """Yields Build objects."""
        base_path_length = len(self.source_directory) + 1

        for (dirpath, dirnames, filenames) in os.walk(self.source_directory):
            logger.debug('Directory %s contains: subdirectories %s, files %s',
                          dirpath, dirnames, filenames)
            subdirectory = dirpath[base_path_length:]
            files_to_build = self.get_files_to_build(subdirectory, filenames)
            logger.debug('Files to build in this directory %s ', dict(files_to_build))

            for base_name, files in files_to_build.items():
                yield Build(subdirectory, base_name, files)

    def run(self):
        for build in self.builds_generator():
            logger.debug('Received Build object: subdirectory %s, base_name %s, files %s',
                         build.subdirectory, build.base_name, build.files)
