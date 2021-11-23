import os
import subprocess
import fnmatch
from ..module import Module



class ExecWithModule(Module):
    """Executes specified executable files using the defined commands to
    produce the input instead of just reading them.

    Example module definition:

        {
            "name": "list_headers",
            "config": {
                "mapping": {
                    "*.py": "python %s",
                    "*.sh": "bash %s"
                }
            }
        }

    """

    def make_read_function(self, command):
        def read(path):
            cwd = os.path.dirname(path)
            cmd = command % path
            r = subprocess.check_output(cmd, shell=True, cwd=cwd,
                                        universal_newlines=True)
            return r.splitlines()
        return read

    def should_exec_with(self, path, module_config):
        """Returns a command which should be executed on the provided file.

        path: Path to the file relative to the source directory root.
        """
        for pattern, command in self.config_get(module_config, 'mapping', {}).items():
            if fnmatch.fnmatch(path, pattern):
                return command
        raise KeyError('exec_with mapping not found: %s' % path )

    def execute(self, build, module_config):
        command = self.should_exec_with(build.input_path, module_config)
        read = self.make_read_function(command)
        build.read = read
