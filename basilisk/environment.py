import copy
import logging
import os
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

    def __init__(self, source_directory, output_directory, templates=None,
                 config=None, builds=None):
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.templates = templates
        self.config = copy.deepcopy(config) or Config()
        self.builds = copy.deepcopy(builds) or []

    def get_context(self, build):
        content, parameters = build.read(self)
        context = {
            'content': content,
            'parameters': parameters,
            'config': self.config,
        }
        return context


class Build(object):
    """Represents one conversion from an input file to an output file.

    input_path: path to the input file relative to the source directory.
    output_path: path to the output file relative to the output directory.
    """

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def __repr__(self):
        return '<%s.%s %s->%s>' % (self.__module__, self.__class__.__name__,
                                   self.input_path, self.output_path)

    def read_parameter(self, line):
        """Reads a single parameter from a line.

        line: string.
        """
        line = line.split(':', 1)
        if len(line) > 1:
            key, value = [element.strip() for element in line]
            return {key: value}
        return {}

    def read(self, environment):
        """Reads content and parameters from the input file.

        environment: Environment object.
        """
        parameters = {}
        content = ''
        path = os.path.join(environment.source_directory, self.input_path)
        with open(path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if not content:
                parameter = self.read_parameter(line)
                if parameter:
                    parameters.update(parameter)
                    continue
            content += line
        return (content, parameters)

    def write(self, environment, content):
        """Writes content to the output file.
        
        environment: Environment object.
        content: This will be written to the output file, most likely a result
                 of template rendering.
        """
        path = os.path.join(environment.output_directory, self.output_path)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, 'w') as f:
            f.write(content)
