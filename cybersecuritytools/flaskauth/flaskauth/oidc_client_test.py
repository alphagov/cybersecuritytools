import json
import os

import pytest
import requests_mock
from jsonlogger import LOG

from .tests import stubs
from .static_site_wrapper_app import bootstrap
from .oidc_client import get_host, get_client


@pytest.mark.usefixtures("test_ssm_parameters")
def test_get_host(test_ssm_parameters):
    ssm_prefix = os.environ.get("SSM_PREFIX")
    stubber = stubs.mock_config_load_ssm_parameters(ssm_prefix, test_ssm_parameters)

    with stubber, requests_mock.Mocker():
        app = bootstrap()
        with app.test_request_context("/"):
            host = get_host()
            assert host == "http://localhost/"


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