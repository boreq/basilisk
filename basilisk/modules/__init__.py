class Module(object):
    """Module."""

    def __init__(self, config, source_directory, destination_directory):
        self.config = config
        self.source_directory = source_directory
        self.destination_directory = destination_directory

        self.logger_name = 'module %s' % self.__class__.name
        self._logger = None

    @property
    def logger(self):
        if not self._logger:
            import logging
            self._logger = logging.getLogger(self.__class__.name)
        return self._logger

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
