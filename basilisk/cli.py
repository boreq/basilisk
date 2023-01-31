import click
import logging
from .builder import Builder
from .server import Server
from .helpers import import_by_name


LOG_FORMAT = '%(levelname)s: %(message)s'
DEBUG_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logger = logging.getLogger('cli')


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    """Basilisk is a static website generator."""
    ctx.obj = {
        'DEBUG': debug
    }
    log_format = (debug and DEBUG_LOG_FORMAT) or LOG_FORMAT
    log_level = (debug and logging.DEBUG) or logging.INFO
    logging.basicConfig(format=log_format, level=log_level)


@cli.command()
@click.argument('source_directory', type=click.Path(exists=False, resolve_path=True))
@click.argument('output_directory', type=click.Path(resolve_path=True))
@click.option('--progress/--no-progress', default=False)
@click.pass_context
def build(ctx, source_directory, output_directory, progress):
    """Builds your website into the output directory."""
    try:
        builder = Builder(source_directory, output_directory, progress=progress)
        builder.run()
    except Exception as e:
        logger.critical(e)
        if ctx.obj['DEBUG']:
            raise


@cli.command()
@click.argument('source_directory', type=click.Path(exists=False, resolve_path=True))
@click.pass_context
@click.option('--host', type=str)
@click.option('--port', type=int)
@click.option('--progress/--no-progress', default=False)
def serve(ctx, source_directory, host, port, progress):
    """Builds and serves your website, rebuilding on file changes."""
    kwargs = {}
    if host is not None:
        kwargs['host'] = host
    if port is not None:
        kwargs['port'] = port
    try:
        server = Server(source_directory, progress=progress, **kwargs)
        server.run()
    except Exception as e:
        logger.critical(e)
        if ctx.obj['DEBUG']:
            raise


@cli.command()
@click.argument('module_name')
def show_help(module_name):
    """Displays module help. Use "list modules" to find out which modules are
    available.
    """
    try:
        import_name = 'basilisk.modules.' + module_name
        module_class = import_by_name(import_name)
        text = module_class.get_help()
        print(text)
    except:
        # TODO: try load an external module.
        raise


@cli.command()
def list_modules():
    """Displays a list of all built in modules."""
    found_modules = []
    from . import modules
    from .module import Module
    for key in dir(modules):
        if not key.startswith('_'):
            v = getattr(modules, key)
            if issubclass(v, Module) and v is not Module:
                found_modules.append(key)

    for name in sorted(found_modules):
        print('{name}'.format(name=name))
