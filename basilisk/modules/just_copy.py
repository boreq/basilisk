import os
import shutil
import types
from ..module import Module


class JustCopyModule(Module):
    """Copies files that have paths ending with specified strings instead of
    building them.
    
    This module doesn't require any additional configuration.
    """

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

    def execute(self, build):
        build.output_path = build.input_path
        method = self.make_method(build)
        build.just_copy = True
        build.execute = types.MethodType(method, build)
