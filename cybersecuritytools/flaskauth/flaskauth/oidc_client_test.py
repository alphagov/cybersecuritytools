import json
import os

import pytest
import requests_mock
from jsonlogger import LOG

from .conftest import get_oidc_root
from .oidc_client import (
    CONFIG,
    get_client,
    get_host,
    get_session_state,
    set_oidc_config,
)
from .static_site_wrapper_app import bootstrap
from .tests import stubs


@pytest.mark.usefixtures("test_ssm_parameters")
def test_get_host(test_ssm_parameters):
    ssm_prefix = os.environ.get("SSM_PREFIX")
    stubber = stubs.mock_config_load_ssm_parameters(ssm_prefix, test_ssm_parameters)

    with stubber, requests_mock.Mocker():
        app = bootstrap()
        with app.test_request_context("/"):
            host = get_host()
            assert host == "http://localhost/"


def test_set_oidc_config():
    oidc_root = get_oidc_root()
    set_oidc_config(
        endpoint=oidc_root,
        client_id="client",
        client_secret="secret",
    )
    assert CONFIG["endpoint"] == oidc_root
    assert CONFIG["client_id"] == "client"
    assert CONFIG["client_secret"] == "secret"
    assert CONFIG["scope"] == "openid profile email roles"
    set_oidc_config(
        endpoint=oidc_root,
        client_id="client",
        client_secret="secret",
        scope="openid email",
    )
    assert CONFIG["scope"] == "openid email"


@pytest.mark.usefixtures("openid_config", "test_ssm_parameters")
def test_get_client(openid_config, test_ssm_parameters):
    ssm_prefix = os.environ.get("SSM_PREFIX")
    stubber = stubs.mock_config_load_ssm_parameters(ssm_prefix, test_ssm_parameters)

    with stubber, requests_mock.Mocker() as mock_requests:
        config_file = json.loads(openid_config)
        app = bootstrap()
        oidc_root = app.config["oidc_endpoint"]
        LOG.debug(oidc_root)
        config_url = f"{oidc_root}.well-known/openid-configuration"
        mock_requests.get(config_url, text=openid_config)
        client = get_client()
        assert client.authorization_endpoint == config_file["authorization_endpoint"]


@pytest.mark.usefixtures("test_ssm_parameters")
def test_get_session_state(test_ssm_parameters):
    ssm_prefix = os.environ.get("SSM_PREFIX")
    stubber = stubs.mock_config_load_ssm_parameters(ssm_prefix, test_ssm_parameters)

    with stubber, requests_mock.Mocker():
        app = bootstrap()
        with app.test_request_context("/"):
            state_1 = get_session_state()
            state_2 = get_session_state()
            assert (
                state_1 == state_2
            ), "Repeated calls should return the same state value"
            state_3 = get_session_state(True)
            assert state_2 != state_3, "Forcing renew should generate a different value"
            state_4 = get_session_state()
            assert (
                state_3 == state_4
            ), "After a forced renew, subsequent calls should result in the same value"
