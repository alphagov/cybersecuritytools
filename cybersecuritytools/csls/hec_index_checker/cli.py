import click

from .hec_index_checker import hec_index_checker


@click.command()
@click.option("--accounts", required=True, help="Accounts TOML path")
@click.option("--token", required=True, help="Token name to check")
@click.option("--ssm", required=True, help="SSM root path")
def check_hec_token(accounts: str, token: str, ssm: str) -> None:
    if not hec_index_checker(accounts, token, ssm):
        sys.exit("Splunk HEC token does not have all indexes required by CSLS.")
