from typing import Any, Dict

import pytest


@pytest.fixture()
def kid() -> str:
    "The Key ID we expect for the above public key"
    return "307a30c3-8280-4ff5-a78d-6bc5263ffbe8"


@pytest.fixture()
def request_home() -> Dict[str, Any]:
    group = "target_group_x/123456"
    account = "123456789012"
    service = "elasticloadbalancing"
    target_group = f"arn:aws:{service}:eu-west-2:{account}:targetgroup/{group}"
    user_agent = "Mozilla/5.0"
    return {
        "requestContext": {"elb": {"targetGroupArn": target_group}},
        "httpMethod": "GET",
        "path": "/",
        "queryStringParameters": {},
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.5",
            "host": "test.gds-cyber-security.digital",
            "upgrade-insecure-requests": "1",
            "user-agent": user_agent,
            "x-forwarded-for": "81.104.91.14",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "body": "",
        "isBase64Encoded": True,
    }
