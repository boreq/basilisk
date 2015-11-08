import html
import markdown
import os
import subprocess
from . import Module


def troff_to_txt(text, macro='man'):
    command = 'nroff -%s | col -bx' % macro
    r = subprocess.check_output(command, shell=True, input=text, universal_newlines=True)
    r = html.escape(r)
    return r


class ManualsModule(Module):
    """Incjects a processor which converts troff files to plaintext. This is
    performed on files which are in a directory which path is in the list
    `manuals` in the config file.
    """

    priority = -5

    def make_processor(self, macro):
        def processor(content, *args, **kwargs):
            return troff_to_txt(content, macro)
        return processor

    def execute(self, builds):
        for build in builds:
            for macro, paths in self.builder.config['manuals'].items():
                for path in paths:
                    # make sure that we don't match files by accident
                    # eg file /path/dir.ext would match with dir /path/dir
                    if not path.endswith(os.sep):
                        path += os.sep
                    pre = os.path.commonprefix([build.input_path, path])
                    if pre == path:
                        processor = self.make_processor(macro)
                        build.processors.append(processor)
