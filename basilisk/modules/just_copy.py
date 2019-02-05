import os
import shutil
import types
from ..module import Module


class JustCopyModule(Module):
    """Copies files that have paths ending with specified strings instead of
    building them.
    
    This module doesn't require any additional configuration.
    """

    def make_method_execute(self, build):
        def execute(self, config, source_directory, output_directory):
            inpath = os.path.join(source_directory, build.input_path)
            outpath = os.path.join(output_directory, build.output_path)
            outdir = os.path.dirname(outpath)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            shutil.copyfile(inpath, outpath)
        return execute

    def make_method_read(self):
        def read(self, *args, **kwargs):
            return []
        return read

    def execute(self, build):
        build.output_path = build.input_path
        method_execute = self.make_method_execute(build)
        build.execute = types.MethodType(method_execute, build)
        method_read = self.make_method_read()
        build.read = types.MethodType(method_read, build)
