from . import Module


class HtmlModule(Module):
    """Simply runs .html files through templates and copy them otherwise
    unchanged.
    """

    def get_context(self, environment, build):
        """Gets the context which is passed to the renered template."""
        return environment.get_context(build)

    def execute(self, environment):
        for build in environment.builds:
            if build.input_path.endswith('.html'):
                self.logger.debug('Building %s', build)
                context = self.get_context(environment, build)
                content = environment.templates.render(build.template_path, context)
                build.write(environment, content)
