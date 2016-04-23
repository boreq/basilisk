import logging
import os
import subprocess
import shutil


logger = logging.getLogger('builder')


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
        # str processor(str content, dict context)
        self.processors = []

        # Additional context which will be passed to processors.
        # See Build.get_context and Build.execute.
        self.additional_context = {}

        # If this is true the whole file will be copied without any modifications.
        # Processors will not run in this instance.
        self.just_copy = False

    def __str__(self):
        return '%s->%s' % (self.input_path, self.output_path)

    def __repr__(self):
        return '<%s.%s %s>' % (self.__module__, self.__class__.__name__,
                               self.__str__())

    def read_parameter(self, line):
        """Reads a parameter from a line of text. Parameters are structured in
        the following form and can be defined at the top of the source file:

            parameter_name: value

        Parameters defined like that are passed in the to the processors in the
        context as a dictionary called `parameters` with names of the parameters
        as keys.

        line: string.
        """
        line = line.split(':', 1)
        if len(line) > 1:
            key, value = [element.strip() for element in line]
            return {key: value}
        return {}

    def read(self, path):
        """Reads and returns the content of the input file.

        path: absolute path to the input file.
        """
        with open(path, 'r') as f:
            try:
                return f.readlines()
            except:
                logger.error('Error in "%s". Is the file encoded in UTF-8, the only sane encoding format?', self.input_path)
                raise

    def parse_lines(self, lines):
        """Parses the lines (presumably from the input file). First lines
        containing the ':' characters are intepreted as `key: value` pairs.
        Those pais populate the second field of the returned tuple. Everything
        else after those `key: value` pairs is considered to be the  content of
        the file and returned as the first element of a tuple. Parameters must
        be separated from content with a blank line or the first line of content
        can't contain a ':' character.
        """
        parameters = {}
        content = ''
        for line in lines:
            if not content:
                parameter = self.read_parameter(line)
                if parameter:
                    parameters.update(parameter)
                    continue
            content += line

        if content.startswith('\r\n'):
            content = content[2:]
        else:
            if content.startswith('\n'):
                content = content[1:]

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

    def get_context(self, parameters, config):
        """Creates the context which is passed to the processors. The context
        contains the parameters defined at the top of the source file, provided
        config and additional context defined by the modules.
        """
        context = {
            'parameters': parameters,
            'config': config,
        }
        context.update(self.additional_context)
        return context

    def execute(self, config, source_directory, output_directory):
        """Runs the build.

        1. If self.just_copy is set just copies input file to output file
           without altering it.
        2. If not it reads the input file, runs the content through processors
           and saves it in the output file.
        """
        inpath = os.path.join(source_directory, self.input_path)
        indir = os.path.dirname(inpath)
        outpath = os.path.join(output_directory, self.output_path)
        outdir = os.path.dirname(outpath)

        if self.just_copy:
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            shutil.copyfile(inpath, outpath)
        else:
            lines = self.read(inpath)
            content, parameters = self.parse_lines(lines)
            for p in self.processors:
                context = self.get_context(parameters, config)
                content = p(content, context)
            self.write(output_directory, content)
