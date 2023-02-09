import logging
import os


logger = logging.getLogger('build')


class Build(object):
    """Represents one conversion from an input file to an output file.

    input_path: path to the input file relative to the source directory.
    output_path: path to the output file relative to the output directory.
    """

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

        # A list of functions which will be used to process the contents of the
        # input file before saving it in the output file. Think about this in
        # terms of running the input through a series of pipes.
        # Expected function signature:
        # processor(content: str, context: dict) -> str
        self.processors = []

        # Additional context which will be passed to processors.
        # See Build.get_context and Build.execute.
        self.additional_context = {}

    def __str__(self):
        return '%s->%s' % (self.input_path, self.output_path)

    def __repr__(self):
        return '<%s.%s %s>' % (self.__module__, self.__class__.__name__,
                               self.__str__())

    def read(self, path) -> bytes:
        """Reads and returns the lines of the input file.

        path: absolute path to the input file.
        """
        with open(path, 'rb') as f:
            return f.read()

    def extract_parameters(self, content: bytes):
        """Parses the content (presumably from the input file). First lines
        containing the ':' characters are intepreted as `key: value` pairs.
        Those pairs populate the second field of the returned tuple. Everything
        else after those `key: value` pairs is considered to be the content of
        the file and returned as the first element of a tuple. Parameters must
        be separated from content with a blank line or the first line of
        content can't contain a ':' character.

        content: bytes most likely loaded from the input file.
        """
        try:
            lines = content.decode().splitlines(True)
        except UnicodeDecodeError:
            return content, {}

        parameters = {}
        remaining_content = ''
        for line in lines:
            if not remaining_content:
                parameter = self.read_parameter(line)
                if parameter:
                    parameters.update(parameter)
                    continue
            remaining_content += line

        if remaining_content.startswith('\r\n'):
            remaining_content = remaining_content[2:]
        else:
            if remaining_content.startswith('\n'):
                remaining_content = remaining_content[1:]

        return (remaining_content.encode(), parameters)

    def read_parameter(self, line):
        """Reads a parameter from a line of text. Parameters are structured in
        the following form and can be defined at the top of the source file:

            parameter_name: value

        Parameters defined like that are passed to the processors in the
        context as a dictionary called `parameters` with names of the
        parameters as keys.

        line: string.
        """
        line = line.split(':', 1)
        if len(line) > 1:
            key, value = [element.strip() for element in line]
            return {key: value}
        return {}

    def write(self, output_directory, content: bytes):
        """Writes content to the output file.

        content: This will be written to the output file.
        """
        path = os.path.join(output_directory, self.output_path)
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(content)

    def get_context(self, parameters, config):
        """Creates the context which is passed to the processors. The context
        contains the parameters defined at the top of the source file, provided
        config and additional context defined by the modules.
        """
        context = {
            'parameters': parameters,
            'config': config,
            'directory': os.path.dirname(self.output_path),
        }
        context.update(self.additional_context)
        return context

    def execute(self, config, source_directory, output_directory):
        """Runs the build. Reads the input file, runs the content through
        processors and saves it in the output file.
        """
        inpath = os.path.join(source_directory, self.input_path)
        content = self.read(inpath)
        content, parameters = self.extract_parameters(content)
        for p in self.processors:
            context = self.get_context(parameters, config)
            content = p(content, context)
        self.write(output_directory, content)
