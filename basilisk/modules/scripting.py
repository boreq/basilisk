import subprocess
from ..module import Module


class ScriptingModule(Module):
    """Executes scripts during the build process. This can allow you to
    implement extra build steps, for example building CSS or JS files.
    Additional variables can be injected as script parameters using two
    placeholder names `${source_directory}` and `${output_directory}`. Those
    will be replaced with proper paths during script execution using simple
    string replacement. The scripts added to the list will be executed before
    compiling the actual project every time you run `basilisk build` or
    `basilisk serve`.

    Example config:

        {
            "scripts": [
                "./path_to_your_script.sh",
                "./script.sh ${source_directory} ${output_directory}"
            ]
        }

    """

    def get_scripts(self, module_config):
        scripts = self.config_get(module_config, 'scripts', [])
        if len(scripts) == 0:
            self.logger.warning('no scripts defined, did you configure "scripting"?')
        return scripts

    def replace_placeholders(self, command):
        command = command.replace('${source_directory}', self.builder.source_directory)
        command = command.replace('${output_directory}', self.builder.output_directory)
        return command

    def run_script(self, command):
        r = subprocess.run(command, shell=True)
        r.check_returncode()

    def process(self, builds, module_config):
        for command in self.get_scripts(module_config):
            command = self.replace_placeholders(command)
            self.logger.debug('Running: {}'.format(command))
            self.run_script(command)
