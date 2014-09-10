import copy
import os
from . import Module
from ..templates import InternationalizedJinja2Templates


class InternationalizationModule(Module):
    """Adds i18n support. While preprocessing the list of environments it
    creates a copies of each environment. Each copy renders a different locale
    to a different directory. The files must be called in the following form:
    `name.locale.ext`. For example: `about.en.html`.

    Accepted config keys:
        i18n_languages: list of languages to render.
        i18n_translations_directory: relative path to the directory containing
                                     translation files.
    """

    priority = -20

    def config_or_fail(self, config, key):
        try:
            return config[key]
        except KeyError:
            raise ValueError('You must define `%s` in your config.' % key)

    def load(self, builder):
        self.languages = self.config_or_fail(builder.config, 'i18n_languages')
        self.translations_directory = self.config_or_fail(builder.config, 'i18n_translations_directory')

        def ignore_translations(path):
            if os.path.commonprefix([self.translations_directory, path]):
                return True
        builder.ignored.append(ignore_translations)

    def split_path(self, path):
        head, tail = os.path.split(path)
        base_name, ext = os.path.splitext(tail)
        core_name, lang = os.path.splitext(base_name)
        return (head, core_name, lang.strip('.'), ext)

    def new_templates(self, templates, locale, translations_directory):
        new = InternationalizedJinja2Templates(
            templates.template_directory,
            base_template_name=templates.base_template_name,
            locale=locale,
            translations_directory=translations_directory
        )
        return new 

    def preprocess(self, environment_list):
        new_list = []
        for environment in environment_list:
            for language in self.languages:
                new_env = copy.deepcopy(environment)
                new_env.output_directory = os.path.join(new_env.output_directory,
                                                        language)
                new_builds = []
                for build in new_env.builds:
                    head, core_name, lang, ext = self.split_path(build.output_path)
                    if lang == language:
                        build.output_path = os.path.join(head, core_name + ext)
                        new_builds.append(build)
                new_env.builds = new_builds
                translations_directory = os.path.join(
                    environment.source_directory,
                    self.translations_directory
                )
                new_env.templates = self.new_templates(
                    environment.templates,
                    locale=language,
                    translations_directory=translations_directory
                )
                new_list.append(new_env)
        return new_list
