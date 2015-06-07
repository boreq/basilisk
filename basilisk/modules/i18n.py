import copy
import os
from . import Module
#from ..templates import InternationalizedJinja2Templates


class InternationalizationModule(Module):
    """Adds i18n support. While preprocessing the list of environments it
    creates a copy of each environment for each language. Each copy renders a
    different locale to a different directory. The input files must be named in
    the following form: `name.locale.ext`. For example: `about.en.html`.

    Accepted config keys:
        i18n_languages: list of languages to render.
        i18n_translations_directory: relative path to the directory containing
                                     translation files.
    """

    priority = -20

    def config_or_fail(self, config, key):
        """Gets the key from a config dictionary or fails with a nice error
        message.
        """
        try:
            return config[key]
        except KeyError:
            raise ValueError('You must define `%s` in your config.' % key)

    def load(self, builder):
        self.languages = self.config_or_fail(builder.config, 'i18n_languages')
        self.translations_directory = self.config_or_fail(builder.config,
                                                          'i18n_translations_directory')

        # Builder should ignore translations directory.
        def ignore_translations(path):
            if os.path.commonprefix([self.translations_directory, path]):
                return True
        builder.ignored.append(ignore_translations)

    def split_path(self, path):
        """Splits the path so that `subdirectory/name.locale.ext` results in
        `('subdirectory/', 'name', 'locale', '.ext')`.
        """
        head, tail = os.path.split(path)
        base_name, ext = os.path.splitext(tail)
        core_name, locale = os.path.splitext(base_name)
        return (head, core_name, locale.strip('.'), ext)

    def new_templates(self, templates, locale, translations_directory):
        """Creates new instance of templates with i18n support from normal
        templates.
        """
        new = InternationalizedJinja2Templates(
            templates.template_directory,
            base_template_name=templates.base_template_name,
            locale=locale,
            translations_directory=translations_directory
        )
        return new 

    def create_new_environment(self, base_environment, language):
        """Creates a new environment localized in the given language."""
        environment = copy.deepcopy(base_environment)
        environment.output_directory = os.path.join(environment.output_directory,
                                                    language)
        # Builds.
        builds = []
        for build in environment.builds:
            head, core, locale, ext = self.split_path(build.output_path)
            if locale == language:
                # Fix output path.
                build.output_path = os.path.join(head, core + ext)
                # Fix template path.
                t_head, t_core, t_locale, t_ext = self.split_path(build.template_path)
                build.template_path = os.path.join(t_head, t_core + t_ext)
                builds.append(build)
        environment.builds = builds

        # Templates.
        translations_directory = os.path.join(base_environment.source_directory,
                                              self.translations_directory)
        environment.templates = self.new_templates(
            environment.templates,
            locale=language,
            translations_directory=translations_directory
        )
        return environment

    def preprocess(self, environment_list):
        new_envs = []
        for environment in environment_list:
            for language in self.languages:
                new_env = self.create_new_environment(environment, language)
                new_envs.append(new_env)
        return new_envs
