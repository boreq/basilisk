import click
import logging
from .builder import Builder

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--verbosity', type=click.Choice(['warning', 'info', 'debug']), default='warning')
@click.pass_context
def cli(ctx, debug, verbosity):
    numeric_level = getattr(logging, verbosity.upper(), None)
    logging.basicConfig(format=LOG_FORMAT, level=numeric_level)
    ctx.obj['DEBUG'] = debug


@cli.command()
@click.pass_context
@click.argument('source_directory', type=click.Path(exists=True, resolve_path=True))
@click.argument('destination_directory', type=click.Path(resolve_path=True))
def build(ctx, source_directory, destination_directory):
    """Builds the project."""
    logging.debug('Debug is %s', ctx.obj['DEBUG'] and 'on' or 'off')
    logging.debug('Source directory is %s', source_directory)
    logging.debug('Destination directory is %s', destination_directory)

    builder = Builder(source_directory, destination_directory)
    builder.run()
