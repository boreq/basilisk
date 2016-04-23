import os
import subprocess
from . import Module



class ExecWithModule(Module):
    """Executes specified executable files using the defined commands to produce
    the input instead of just reading them.

    Example config:

        {
            "exec": {
                ".py": "python %s",
                ".sh": "bash %s"
            }
        }

    """

    priority = -20

    def make_read_function(self, command):
        def read(path):
            cwd = os.path.dirname(path)
            cmd = command % path
            r = subprocess.check_output(cmd, shell=True, cwd=cwd,
                                        universal_newlines=True)
            return r.splitlines()
        return read

    def should_exec_with(self, path):
        """Returns a command which should be executed on the provided file.

        path: Path to the file relative to the source directory root.
        """
        for ext, command in self.builder.config.get('exec', {}).items():
            if path.endswith(ext):
                return command
        return None

    def execute(self, builds):
        for build in builds:
            command = self.should_exec_with(build.input_path)
            if command is not None:
                read = self.make_read_function(command)
                build.read = read
