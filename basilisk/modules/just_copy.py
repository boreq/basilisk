import os
import shutil
import types
from . import Module


class JustCopyModule(Module):
    """Injects a module which escapes all special HTML characters present in
    the input files. This module is useful to escape plaintext files which can
    contain special characters. Remember to exclude file extensions in the
    config to prevent this module from escaping certain files if you want the
    HTML they contain to be rendered.

    Example config:

        {
            "dont_escape": [".html"]
        }

    """

    priority = -25

    def should_just_copy(self, path):
        """Returns True if a file which is stored under the provided path
        should be copied without any changes.

        path: Path to the file relative to the source directory root.
        """
        for ext in self.builder.config.get('just_copy', []):
            if path.endswith(ext):
                return True
        return False

    def make_method(self, build):
        m = build.execute
        def execute(self, config, source_directory, output_directory):
            if not getattr(self, 'just_copy', False):
                return m(config, source_directory, output_directory)
            inpath = os.path.join(source_directory, build.input_path)
            outpath = os.path.join(output_directory, build.output_path)
            outdir = os.path.dirname(outpath)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            shutil.copyfile(inpath, outpath)
        return execute

    def execute(self, builds):
        for build in builds:
            build.just_copy = self.should_just_copy(build.input_path)
            if build.just_copy:
                build.output_path = build.input_path
                method = self.make_method(build)
                build.execute = types.MethodType(method, build)
