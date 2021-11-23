import subprocess
import fnmatch
from ..module import Module


def troff_to_txt(text, macro='man'):
    command = 'nroff -%s | col -bx' % macro
    r = subprocess.check_output(command, shell=True, input=text, universal_newlines=True)
    return r


class ManualsModule(Module):
    """Converts troff files to plaintext. This is performed on files which are
    in the directories defined in the config file. The keys of the dictionary
    "manuals" defined in the config file should contain the names of troff
    macros which will be used to process the files. The value of each key
    should be a list of directories. All files present in those directories
    will be converted.

    Example config:

        {
            "macros": {
                "man": [
                    "manuals/9front/1/*"
                ]
            }
        }

    """

    def make_processor(self, macro):
        def processor(content, *args, **kwargs):
            return troff_to_txt(content, macro)
        return processor

    def get_macro(self, build, module_config):
        for macro, patterns in self.config_get(module_config, 'macros', {}).items():
            for pattern in patterns:
                if fnmatch.fnmatch(build.input_path, pattern):
                    return macro
        raise KeyError('macro not found for %s', build.input_path)

    def execute(self, build, module_config):
        macro = self.get_macro(build, module_config)
        processor = self.make_processor(macro)
        build.processors.append(processor)
