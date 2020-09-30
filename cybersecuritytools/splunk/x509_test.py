from os.path import isfile

import pytest

from .x509 import CertBundle, RequestsFingerPrintAdapterCertificates


@pytest.fixture
def cert_bundle() -> CertBundle:
    host_cert = "AAAA"
    ca_cert = "BBBB"
    return CertBundle(host_cert, ca_cert)


@pytest.fixture
def rfpac(cert_bundle: CertBundle) -> RequestsFingerPrintAdapterCertificates:
    return RequestsFingerPrintAdapterCertificates(cert_bundle)


def test_init_creates_cert_file(rfpac: RequestsFingerPrintAdapterCertificates) -> None:
    assert rfpac.cert_file.name
    assert isfile(rfpac.cert_file.name)


def test_cert_file(rfpac: RequestsFingerPrintAdapterCertificates) -> None:
    with open(rfpac.cert_file.name) as f:
        contents = f.read()
    assert "-----BEGIN CERTIFICATE-----" in contents
    assert "AAAA" in contents
    assert "BBBB" in contents
    assert "-----END CERTIFICATE-----" in contents


def test_host_certificate_fingerprint(
    rfpac: RequestsFingerPrintAdapterCertificates,
) -> None:
    assert (
        rfpac.host_certificate_fingerprint()
        == "709e80c88487a2411e1ee4dfb9f22a861492d20c4765150c0c794abd70f8147c"
    )


def test_ca_certificate_fingerprint(
    rfpac: RequestsFingerPrintAdapterCertificates,
) -> None:
    assert (
        rfpac.ca_certificate_fingerprint()
        == "09c08a63fc2b11a50cf88eb6f6c062c727964a0c828808fe46c740af3a33897a"
    )
