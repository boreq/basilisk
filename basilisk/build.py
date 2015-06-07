import os
from .helpers import replace_ext


class Build(object):
    """Represents one conversion from an input file to an output file.

    input_path: path to the input file relative to the source directory.
    output_path: path to the output file relative to the output directory.
    """

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        # List of functions which will be used to process the content of the
        # input file before saving it in the output file.
        # Expected function signature:
        # str process(str content, dict parameters)
        self.processors = []

    def __str__(self):
        return '%s->%s' % (self.input_path, self.output_path)

    def __repr__(self):
        return '<%s.%s %s>' % (self.__module__, self.__class__.__name__,
                                  self__str__())

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

    def read(self, source_directory):
        """Reads content and parameters from the input file."""
        parameters = {}
        content = ''
        path = os.path.join(source_directory, self.input_path)
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

    def write(self, output_directory, content):
        """Writes content to the output file.

        content: This will be written to the output file, most likely a result
                 of template rendering.
        """
        path = os.path.join(output_directory, self.output_path)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, 'w') as f:
            f.write(content)

    def execute(self, source_directory, output_directory):
        content, parameters = self.read(source_directory)
        for p in self.processors:
            content = p(content, parameters)
        self.write(output_directory, content)
