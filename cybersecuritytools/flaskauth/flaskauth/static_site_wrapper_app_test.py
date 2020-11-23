import pytest
import json

from .static_site_wrapper_app import app  # noqa

app.config["SECRET_KEY"] = "testnotrandom"

@pytest.fixture(scope="session")
def authenticated():
    """Setup a flask test client. This is used to connect to the test
    server and make requests.
    """

    app.config["TESTING"] = True
    app.config["verify_oidc"] = False
    authenticated = app.test_client()
    return authenticated


@pytest.fixture(scope="session")
def unauthenticated():
    """Setup a flask test unauthenticated. This is used to connect to the test
    server and make requests.
    """

    unauthenticated = app.test_client()
    return unauthenticated


@pytest.fixture(scope="session")
def alb_https_odic_get_root():
    """Load a JSON alb request that has OIDC information in it.
    """
    with open("tests/fixtures/alb_https_oidc_get_root.json", "r") as f:
        return json.load(f)


def test_good_to_go(unauthenticated):
    """Test the '/__gtg' endpoint works and returns the text 'Good to
    Go!'. This is used by the ELB healthcheck.
    """
    result = unauthenticated.get("/__gtg")
    assert b"Good to Go!" in result.data


def test_logout(authenticated):
    """Test the '/logout' endpoint works and returns /login redirect
    """
    result = authenticated.get("/logout")
    assert b"/login" in result.data and 302 == result.status_code
