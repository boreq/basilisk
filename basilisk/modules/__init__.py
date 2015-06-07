"""
    All functionality is implemented by modules. Modules operate on the build
    objects. Original list containing those objects is created in the builder.
    After that `Module.run()` method of all modules is called on that list.
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
        """Run a module

        builds: List of Build objects.
        """
        pass


# Easier import names.
from .templates import TemplatesModule
templates = TemplatesModule

from .pretty_urls import PrettyUrlsModule
pretty_urls = PrettyUrlsModule

from .i18n import InternationalizationModule
i18n = InternationalizationModule
