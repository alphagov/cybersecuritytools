import pytest

from .api import SplunkApi, SplunkCredentials
from .x509 import RequestsFingerPrintAdapterCertificates


@pytest.fixture
def splunk_credentials() -> SplunkCredentials:
    creds = SplunkCredentials(
        hostname="splunkfoo.com",
        port="443",
        username="tester",
        password="foobar123",
    )
    return creds


@pytest.fixture
def splunk_api(
    splunk_credentials: SplunkCredentials, rfpac: RequestsFingerPrintAdapterCertificates
) -> SplunkApi:
    api = SplunkApi(splunk_credentials, rfpac)
    return api


def test_splunk_api_base_url(
    splunk_api: SplunkApi, splunk_credentials: SplunkCredentials
) -> None:
    expected = f"https://{splunk_credentials.hostname}:{splunk_credentials.port}"
    result = splunk_api.base_url()
    assert result == expected
