from typing import Any, Dict

import pytest

from .lambda_handler import lambda_handler


@pytest.mark.usefixtures("request_home")
def get_homepage(request_home: Dict[str, Any]) -> None:
    """
    Run a request through the lambda_handler and save the response for
    later testing.
    """
    response = lambda_handler(request_home, None)
    assert isinstance(response, dict)
    assert "body" in response
    assert "statusCode" in response
    assert "headers" in response
    assert "Content-Type" in response["headers"]
