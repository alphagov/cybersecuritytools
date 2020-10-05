import click

from cybersecuritytools.csls.cli import csls


@click.group()
def cli() -> None:
    pass


# Add new modules here
cli.add_command(csls)
