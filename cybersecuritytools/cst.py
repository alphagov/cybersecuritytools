#! /usr/bin/env python
from sys import exit

import click

from cybersecuritytools.csls.hec_index_checker import hec_index_checker


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--accounts", required=True, help="Accounts TOML path")
@click.option("--token", required=True, help="Token name to check")
@click.option("--ssm", required=True, help="SSM root path")
def check_hec_token(accounts: str, token: str, ssm: str) -> None:
    if not hec_index_checker(accounts, token, ssm):
        exit(1)


@cli.command()
def other() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    cli()
