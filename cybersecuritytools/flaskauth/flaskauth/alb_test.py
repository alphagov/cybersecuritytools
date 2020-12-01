import json

import pytest

from .alb import alb_get_user_info, get_kid, get_public_key


@pytest.fixture(scope="session")
def encoded_jwt():
    """This is an encoded_jwt token used for testing"""
    with open("tests/fixtures/alb_https_oidc_get_root.json", "r") as f:
        return json.load(f)["headers"]["x-amzn-oidc-data"]


@pytest.fixture(scope="session")
def elb_public_key() -> str:
    """A public key from an ALB. These rotate so we have it for data
    consistency.
    """
    with open("tests/fixtures/alb_public_key.txt", "r") as f:
        return f.read()


@pytest.fixture(scope="session")
def kid() -> str:
    "The Key ID we expect for the above public key"
    return "307a30c3-8280-4ff5-a78d-6bc5263ffbe8"


def test_get_kid(encoded_jwt: str, kid: str) -> None:
    """Check the Key ID from the encoded_jwt token is what we expect"""
    result = get_kid(encoded_jwt)
    assert kid == result
