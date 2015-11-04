import click
import logging
from .builder import Builder


LOG_FORMAT = '%(levelname)s: %(message)s'
DEBUG_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logger = logging.getLogger('cli')


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj = {'DEBUG': debug}
    log_format = (debug and DEBUG_LOG_FORMAT) or LOG_FORMAT
    log_level = (debug and logging.DEBUG) or logging.INFO
    logging.basicConfig(format=log_format, level=log_level)


@cli.command()
@click.argument('source_directory', type=click.Path(exists=False, resolve_path=True))
@click.argument('output_directory', type=click.Path(resolve_path=True))
@click.pass_context
def build(ctx, source_directory, output_directory):
    """Builds the project."""
    try:
        builder = Builder(source_directory, output_directory)
        builder.run()
    except Exception as e:
        logger.critical(e)
        if ctx.obj['DEBUG']:
            raise
