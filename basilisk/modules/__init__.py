"""
    All functionality is implemented by modules. Modules operate on the build
    objects. Original list containing those objects is created in the builder.
    After that Module.execute() method of all modules is called on that list.
    See Builder.run() for more information.
"""


class Module(object):
    """Base module class."""

    # Modules with lower priority are executed earlier. By assigning a higher
    # value to a module you can execute it after the modules which produce
    # output it requires.
    priority = 0

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

    def load(self, builder):
        """Called when the module is loaded in the builder.

        builder: a Builder object.
        """
        self.builder = builder

    def execute(self, builds):
        """Runs a module.

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
