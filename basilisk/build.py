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

        # List of functions which will be used to process the content of the
        # input file before saving it in the output file.
        # Basically: input file -> processors -> output file
        # Think about this like about running a stream through pipes.
        # Expected function signature:
        # str process(str content, dict parameters)
        self.processors = []

        # Additional context which will be passed to processors. See Build.execute
        self.additional_context = {}

        # This is populated after init by builder. Modules might need those.
        self.parameters = []

        # If this is true the whole file will be copied without any modifications.
        # Processors will not run in this instance.
        self.just_copy = False

        # If this is not None the file will be executed with the command set
        # in this variable instead of being read directly. This variable can
        # for example be set to `bash %s` or `python %s`.
        self.execute_with = None

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
        """Reads content and parameters from the input file.
        See Build.parse_lines.

        source_directory: path to the source directory with all files.
        """
        path = os.path.join(source_directory, self.input_path)
        with open(path, 'r') as f:
            try:
                lines = f.readlines()
            except:
                logger.error('Error in "%s". Is the file encoded in UTF-8, the only sane encoding format?', self.input_path)
                raise

        return self.parse_lines(lines)

    def parse_lines(self, lines):
        """Parses the lines presumably from the input file. First lines containing
        ':' characters are intepreted as `key: value` pairs. Those pais populate
        the second field of the returned tuple. Everything else below it 
        is considered as content and returned as the first element of a tuple.
        Parameters must be separated from content with a blank line or the first
        line of content can't contain a ':' character.
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

    def execute(self, config, source_directory, output_directory):
        """Runs the build.

        1. If self.just_copy is set just copies input file to output file
           without altering it.
        2. If not if reads the input file (or executes it if self.execute_with
           is set), runs the content through processors and saves it in output
           file.
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
            # Run the file and get stdout or just read it
            if self.exec_with:
                command = self.exec_with % inpath
                r = subprocess.check_output(command, shell=True, cwd=indir, universal_newlines=True)
                content, parameters = self.parse_lines(r)
            else:
                content, parameters = self.read(source_directory)

            for p in self.processors:
                context = {
                    'parameters': parameters,
                    'config': config,
                    'directory': os.path.dirname(self.output_path)
                }
                context.update(self.additional_context)
                content = p(content, context)
            self.write(output_directory, content)
