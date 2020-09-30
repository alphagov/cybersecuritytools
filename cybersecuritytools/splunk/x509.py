import base64
import hashlib
import os
import tempfile
from dataclasses import dataclass

from ..aws.ssm import get_param_from_ssm


@dataclass
class CertBundle:
    host_cert: str
    ca_cert: str


def cert_bundle_new(ssm_root: str) -> CertBundle:
    host_cert = os.environ.get(
        "SPLUNK_HOST_CERT", get_param_from_ssm(f"/{ssm_root}/splunk_host_cert")
    )
    ca_cert = os.environ.get(
        "SPLUNK_CA_CERT", get_param_from_ssm(f"/{ssm_root}/splunk_ca_cert")
    )
    return CertBundle(
        host_cert=host_cert,
        ca_cert=ca_cert,
    )


class RequestsFingerPrintAdapterCertificates:
    def __init__(self, cert_bundle: CertBundle):
        self.cert_bundle = cert_bundle
        self.cert_file = tempfile.NamedTemporaryFile()
        self.write_certificate_file()

    def write_certificate_file(self) -> None:
        armoured_certs = self.certificate_bundle()
        self.cert_file.write(armoured_certs.encode())
        self.cert_file.flush()

    def certificate_bundle(self) -> str:
        """Join multiple certificates into a the CA bundle format"""
        return "".join(
            self.certificate_armour(cert)
            for cert in [self.cert_bundle.ca_cert, self.cert_bundle.host_cert]
        )

    def certificate_armour(self, cert: str) -> str:
        """Add the standard X509 armour to a certificates base64 encoded data."""
        return f"""-----BEGIN CERTIFICATE-----
{cert}
-----END CERTIFICATE-----
"""

    def host_certificate_fingerprint(self) -> str:
        return self.certificate_fingerprint(self.cert_bundle.host_cert)

    def ca_certificate_fingerprint(self) -> str:
        return self.certificate_fingerprint(self.cert_bundle.ca_cert)

    def certificate_fingerprint(self, cert: str) -> str:
        """Generate a sha256 fingerprint from a certificater base64 encdoded
        data for use as the fingerprint in requests_toolbelt.FingerprintAdapter"""
        sha256 = hashlib.sha256()
        sha256.update(base64.b64decode(cert))
        return sha256.hexdigest()

    def cert_filename(self) -> str:
        return self.cert_file.name
