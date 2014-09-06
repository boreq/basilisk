import click
import logging
from .builder import Builder


LOG_FORMAT = '%(levelname)s: %(message)s'
DEBUG_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logger = logging.getLogger('cli')


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--verbosity', type=click.Choice(['warning', 'info', 'debug']), default='info')
@click.pass_context
def cli(ctx, debug, verbosity):
    numeric_level = getattr(logging, verbosity.upper(), None)
    if debug:
        log_format = DEBUG_LOG_FORMAT
    else:
        log_format = LOG_FORMAT
    logging.basicConfig(format=log_format, level=numeric_level)


@cli.command()
@click.pass_context
@click.argument('source_directory', type=click.Path(exists=True, resolve_path=True))
@click.argument('destination_directory', type=click.Path(resolve_path=True))
def build(ctx, source_directory, destination_directory):
    """Builds the project."""
    logger.debug('Source directory is %s', source_directory)
    logger.debug('Destination directory is %s', destination_directory)

    builder = Builder(source_directory, destination_directory)
    builder.run()
