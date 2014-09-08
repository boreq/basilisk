import os
from . import Module


class PrettyUrlsModule(Module):
    """Makes the urls "pretty" by moving all outputs with file not called
    `index` into a subdirectory. For example output called `directory/page.html`
    will be changed to `directory/page/index.html`. That way it will be possible
    to access it simply using `directory/page/`. All `index.html` files are
    unaffected. Watch out for conflicts in situations similar to this one:

        directory_name.html
        directory_name/
            index.html

    In the above scenario output of 'directory_name.html' would be changed
    to 'directory_name/index.html' and outputs would overwrite each other.
    """

    priority = -10

    def preprocess(self, environment_list):
        for environment in environment_list:
            for build in environment.builds:
                head, tail = os.path.split(build.output_path)
                base_name, ext = os.path.splitext(tail)
                if base_name != 'index':
                    self.logger.debug('Changing output of %s', build)
                    build.output_path = os.path.join(head, base_name, 'index' + ext)
        return environment_list
