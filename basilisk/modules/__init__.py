class Module(object):
    """Module."""

    # Modules with lower priority are executed earlier. By assigining a higher
    # value to to a module you can execute it after the modules on which output
    # it depends.
    priority = 0

    def __init__(self, config):
        self.config = config
        self.logger_name = 'module %s' % self.__class__.name
        self._logger = None

    @property
    def logger(self):
        """Use this logger to log messages in the module. It automatically gets
        a right name assinged.
        """
        if not self._logger:
            import logging
            self._logger = logging.getLogger(self.__class__.name)
        return self._logger

    def interested_in(self, path):
        """Return True if this module would like to process the given path. File
        no module is interested in will not be added to the initial environment.

        path: Path to a file realtive to the source_directory root.
        """
        return False

    def preprocess(self, environment_list):
        """Modify the list of environments before executing all modules. This
        function can add new Environment objects to the list or change the
        existing ones.

        environment_list: list of Environment objects.
        """
        return environment_list

    def run(self, environment):
        """Run build of one environment.

        environment: Environment object.
        """
        pass
