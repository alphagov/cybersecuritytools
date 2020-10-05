import click

from .generate_cloudwatch_logs.cli import generate_cloudwatch_logs
from .hec_index_checker.cli import check_hec_token


# Top level module group
@click.group()
def csls() -> None:
    pass


# Module sub groups / commands
csls.add_command(check_hec_token)
csls.add_command(generate_cloudwatch_logs)
