from typing import Any, Set

import requests
from requests.auth import HTTPBasicAuth
from requests_toolbelt.adapters.fingerprint import FingerprintAdapter  # type: ignore

from .credentials import SplunkCredentials
from .x509 import RequestsFingerPrintAdapterCertificates


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
