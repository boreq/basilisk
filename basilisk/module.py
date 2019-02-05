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
        """Returns a key from the config defined for this module in the config
        file. To use this method define self.config_key.
        """
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

        builds: list containing Build objects.
        """
        pass

    def postprocess(self, builds):
        """Executes a postprocessing step.

        builds: list containing Build objects.
        """
        pass

    def execute(self, build):
        """Runs this module on a build.

        build: a Build object.
        """
        pass
