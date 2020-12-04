import os

import pytest
import requests_mock

from .tests import stubs
from .static_site_wrapper_app import bootstrap
from .auth import make_default_response


@pytest.mark.usefixtures("test_ssm_parameters")
def test_make_default_response(test_ssm_parameters):
    ssm_prefix = os.environ.get("SSM_PREFIX")
    stubber = stubs.mock_config_load_ssm_parameters(ssm_prefix, test_ssm_parameters)

    with stubber, requests_mock.Mocker():
        app = bootstrap()
        with app.test_request_context("/"):
            response = make_default_response("/")
            body = response.data.decode()
            assert response.status_code == 200
            assert "text/html" in response.content_type
            assert "Access granted" in body

        with pytest.raises(FileNotFoundError):
            make_default_response("/not-found.html")
