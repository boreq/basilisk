import os
from . import Module


class PrettyUrlsModule(Module):
    """Makes the urls "pretty" by moving all outputs not called `index.html`
    into a subdirectory. For example output called `directory/page.html`
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

    def explode_path(self, path):
        head, tail = os.path.split(path)
        base_name, ext = os.path.splitext(tail)
        return (head, base_name, ext)

    def execute(self, builds):
        for build in builds:
            head, base_name, ext = self.explode_path(build.output_path)
            if base_name != 'index':
                self.logger.debug('Changing output of %s', build)
                build.output_path = os.path.join(head, base_name, 'index' + ext)
