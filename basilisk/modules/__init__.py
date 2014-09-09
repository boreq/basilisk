class Module(object):
    """All functionality is implemented by modules. Modules operate on the
    environment objects. Original list containing one initial environment object
    is created in the builder. After that `Module.preprocess()` method of all
    modules is called on that list. Modules can modify the existing environment
    or create new ones. After all modules preprocess the list `Module.execute()`
    method of each module is called on all environments stored in that list.
    See Builder.run() for more information.
    """

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
        
        builder: Builder object.
        """
        pass

    def preprocess(self, environment_list):
        """Allows the module to modify the list of environments.

        environment_list: list of Environment objects.
        """
        return environment_list

    def execute(self, environment):
        """Execute a build of one environment.

        environment: Environment object.
        """
        pass


# Easier import names.
from .html import HtmlModule
html = HtmlModule

from .pretty_urls import PrettyUrlsModule
pretty_urls = PrettyUrlsModule
