"""
    All functionality is implemented by modules. Modules operate on the build
    objects. Original list containing those objects is created in the builder.
    After that Module.execute() method of all modules is called on that list.
    See Builder.run() for more information.
"""


_sentinel = object()


class Module(object):
    """Base module class."""

    def __init__(self):
        self._logger_name = self.__class__.__name__
        self._logger = None

    def __str__(self):
        return self.__class__.__name__

    @classmethod
    def get_help(cls):
        # It is necessary to fix the indentation of the first line. It is
        # usually inconsitent with the rest of the docstring if PEP 257 is
        # followed (see section "Multi-line Docstrings").
        lines = cls.__doc__.splitlines()
        if len(lines) > 1:
            num_spaces = lines[1].count(' ') - lines[1].lstrip(' ').count(' ')
            lines[0] = ' ' * num_spaces + lines[0]
        return '\n'.join(lines)

    @property
    def logger(self):
        """Use this logger to log messages in the module."""
        if not self._logger:
            import logging
            self._logger = logging.getLogger(self._logger_name)
        return self._logger

    def config_get(self, key, default=_sentinel):
        try:
            return self.builder.config['module_config'][self.config_key][key]
        except KeyError:
            pass

        if not default is _sentinel:
            return default

        raise KeyError

    def load(self, builder):
        """Called when the module is loaded in the builder.

        builder: a Builder object.
        """
        self.builder = builder

    def preprocess(self, builds):
        """Executes a preprocessing step.

        builds: List of Build objects.
        """
        pass

    def postprocess(self, builds):
        """Executes a postprocessing step.

        builds: List of Build objects.
        """
        pass

    def execute(self, build):
        """Runs a module on a build.

        builds: List of Build objects.
        """
        pass


# Easier import names.
from .markdown import MarkdownModule as _MarkdownModule
markdown = _MarkdownModule

from .templates import TemplatesModule as _TemplatesModule
templates = _TemplatesModule

from .pretty_urls import PrettyUrlsModule as _PrettyUrlsModule
pretty_urls = _PrettyUrlsModule

from .listing import ListingModule as _ListingModule
listing = _ListingModule

from .manuals import ManualsModule as _ManualsModule
manuals = _ManualsModule

from .escape import EscapeModule as _EscapeModule
escape = _EscapeModule

from .exec_with import ExecWithModule as _ExecWithModule
exec_with = _ExecWithModule

from .just_copy import JustCopyModule as _JustCopyModule
just_copy = _JustCopyModule

from .blog import BlogModule as _BlogModule
blog = _BlogModule
