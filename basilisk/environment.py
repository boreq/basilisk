import copy
import logging
import os
from .config import Config
from .context import EnvContext
from .helpers import replace_ext


class Environment(object):
    """Holds parameters related to building a list of builds such as config or
    templates.

    source_directory: path to the source directory.
    output_directory: path to the output directory.
    templates: object which inherits from BaseTemplates.
    config: individual config, can be changed later. In the initial Environment
            it is a copy of the builder config.
    """

    def __init__(self, source_directory, output_directory, templates=None,
                 config=None):
        self.source_directory = source_directory
        self.output_directory = output_directory
        self.templates = templates
        self.config = copy.deepcopy(config) or Config()

    def get_context(self, build):
        """Get context passed to the templates when executing a build in this
        environment.

        build: Build object.
        """
        content, parameters = build.read(self)
        context = {
            'content': content,
            'parameters': parameters,
            'config': self.config,
        }
        return context

    def env_context(self):
        return EnvContext(self)


class Build(object):
    """Represents one conversion from an input file to an output file.

    input_path: path to the input file relative to the source directory.
    output_path: path to the output file relative to the output directory.
    """

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        # Path used for selecting the right template. Passed to
        # BaseTemplates._template_name_generator. Module might overwrite that
        # value if it requres a source filename in an unusual format. An example
        # of that is the built in i18n extension which requires locale in the
        # filename. That normally results in matching the wrong template.
        base, ext = os.path.splitext(input_path)
        self.template_path = replace_ext(input_path, ext, '.html')

    def __repr__(self):
        return '<%s.%s %s->%s>' % (self.__module__, self.__class__.__name__,
                                   self.input_path, self.output_path)

    def read_parameter(self, line):
        """Reads a parameter from a line of text. Parameters are structured in
        the following form and can be defined at the top of the source file:

            parameter_name: value

        Parameters defined like that are passed in the template context as
        a dictionary called `parameters` with names of the parameters as keys.

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
