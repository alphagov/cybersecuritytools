from botocore.exceptions import ClientError  # type: ignore

from cybersecuritytools.splunk.api import SplunkApi, SplunkApiError
from cybersecuritytools.splunk.credentials import credentials
from cybersecuritytools.splunk.x509 import (
    RequestsFingerPrintAdapterCertificates,
    cert_bundle_new,
)

from .accountstoml import indexes_from_accounts, load_accounts_loggroup_index_toml


def hec_index_checker(accounts: str, token: str, ssm: str) -> bool:
    """Check that a Splunk HEC token has all indexes required by CSLS.

    accounts: Path to the CSLS `accounts_loggroup_index.toml`
    token: Name of the Splunk HEC token to check against
    ssm: The AWS SSM directory to retrieve the credentials from.

    The SSM directory must have these key/values:
    splunk_hostname
    splunk_port
    splunk_username
    splunk_password
    splunk_host_cert
    splunk_ca_cert

    The function returns `True` if all indexes listed in the TOML file
    are writable by the HEC token.

    A `False` value indicates either an error or the token does not have
    the required indexes.
    """
    try:
        accounts_log_group = load_accounts_loggroup_index_toml(accounts)
    except FileNotFoundError:
        print(f"[!] Can not open TOML file: {accounts}")
        return False

    required_indexes = indexes_from_accounts(accounts_log_group)

    try:
        api_credentials = credentials(ssm, "api")
    except ClientError:
        print("[!] Unable to build Splunk Credentials")
        return False

    try:
        cert_bundle = cert_bundle_new(ssm)
    except ClientError:
        print("[!] Unable to build Splunk certificate bundle")
        return False
    rfpac = RequestsFingerPrintAdapterCertificates(cert_bundle)

    splunk_api = SplunkApi(api_credentials, rfpac)

    try:
        available_indexes = splunk_api.token_indexes(token)
    except SplunkApiError:
        print("[!] Splunk returned a non 200 status code.")
        return False
    except StopIteration:
        print(f"[!] HEC token `{token}` does not exist")
        return False

    if required_indexes.issubset(available_indexes):
        print("[+] HEC token has all required indexes")
        return True
    else:
        print("[!] HEC token does *NOT* have all required indexes!")
        return False
