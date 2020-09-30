import os
from dataclasses import dataclass
from typing import Any, Set

import requests
from requests.auth import HTTPBasicAuth
from requests_toolbelt.adapters.fingerprint import FingerprintAdapter  # type: ignore

from ..aws.ssm import get_param_from_ssm
from .x509 import RequestsFingerPrintAdapterCertificates


@dataclass
class SplunkCredentials:
    hostname: str
    port: str
    password: str
    username: str


def splunk_credentials_new(ssm_root: str) -> SplunkCredentials:
    """Retrieves details for connecting to Splunk. It will use prefer
    local environment variables if configured, or it will fetch the
    parameters from AWS SSM.

    The environment variables are:
    SPLUNK_HOSTNAME
    SPLUNK_PORT
    SPLUNK_USERNAME
    SPLUNK_PASSWORD

    The AWS SSM parameter names are:
    '/{ssm_root}/splunk_hostname'
    '/{ssm_root}/splunk_port'
    '/{ssm_root}/splunk_username'
    '/{ssm_root}/splunk_password'

    If a complete set of credentials can't be collected this function will error.
    """
    hostname = os.environ.get(
        "SPLUNK_HOSTNAME", get_param_from_ssm(f"/{ssm_root}/splunk_hostname")
    )
    port = os.environ.get("SPLUNK_PORT", get_param_from_ssm(f"/{ssm_root}/splunk_port"))
    username = os.environ.get(
        "SPLUNK_USERNAME", get_param_from_ssm(f"/{ssm_root}/splunk_username")
    )
    password = os.environ.get(
        "SPLUNK_PASSWORD", get_param_from_ssm(f"/{ssm_root}/splunk_password")
    )
    return SplunkCredentials(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
    )


class SplunkApiError(Exception):
    pass


class SplunkApi:
    """A class access the Splunk API. It uses certificate pinning to work
    around the self signed certificate on Splunk Cloud."""

    def __init__(
        self,
        credentials: SplunkCredentials,
        rfpac: RequestsFingerPrintAdapterCertificates,
    ):
        self.credentials = credentials
        self.rfpac = rfpac
        self.create_session()

    def base_url(self) -> str:
        return f"https://{self.credentials.hostname}:{self.credentials.port}"

    def create_session(self) -> None:
        self.session = requests.Session()
        self.session.mount(
            self.base_url(),
            FingerprintAdapter(self.rfpac.host_certificate_fingerprint()),
        )

    def get_url(self, url: str) -> Any:
        auth = HTTPBasicAuth(
            self.credentials.username,
            self.credentials.password,
        )
        try:
            response = self.session.get(
                self.base_url() + url,
                auth=auth,
                timeout=5,
                verify=self.rfpac.cert_filename(),
            )
        except requests.exceptions.ConnectTimeout:
            print("[!] Timed out connecting to Splunk API")
            raise

        if response.status_code != 200:
            raise SplunkApiError

        return response

    def get_hec_tokens(self) -> Any:
        """The Splunk users role needs the `dmc_deploy_apps` and
        `dmc_deploy_token_http` capabilities."""
        url = "/services/dmc/config/inputs/-/http?output_mode=json"
        tokens = self.get_url(url).json()
        return tokens

    def get_hec_token(self, token_name: str) -> Any:
        tokens = self.get_hec_tokens()
        token = next(token for token in tokens["entry"] if token["name"] == token_name)
        return token

    def token_indexes(self, token_name: str) -> Set[str]:
        token = self.get_hec_token(token_name)
        token_indexes = set(token["content"]["indexes"].split(","))
        return token_indexes
