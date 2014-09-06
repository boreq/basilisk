import click
import logging
from .builder import Builder


LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logger = logging.getLogger('cli')


@click.group()
@click.option('--verbosity', type=click.Choice(['warning', 'info', 'debug']), default='warning')
@click.pass_context
def cli(ctx, verbosity):
    numeric_level = getattr(logging, verbosity.upper(), None)
    logging.basicConfig(format=LOG_FORMAT, level=numeric_level)


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
