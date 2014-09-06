import copy
from .config import Config


class Environment(object):
    """Holds config and list of builds to be executed. One of those is initially
    crated by the builder and passed to the modules which can modify it or
    create additional environments.

    Passed arguments are deep copied to allow introducing changes independently.

    config: individual config, can be changed later. In the initial Environment
            it is a copy of builder config.
    builds: list of Build objects.
    """

    def __init__(self, source_directory, output_directory, config=None,
                 builds=None):
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.config = copy.deepcopy(config) or Config()
        self.builds = copy.deepcopy(builds) or []


class Build(object):
    """Build object.

    input_path: path to the input file relative to the source directory.
    output_path: path to the output file relative to the output directory.
    """

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def __repr__(self):
        return '<%s.%s %s->%s>' % (self.__module__, self.__class__.__name__,
                                   self.input_path, self.output_path)
