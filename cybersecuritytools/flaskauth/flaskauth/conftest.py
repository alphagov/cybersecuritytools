from typing import Any, Dict

import pytest


@pytest.fixture()
def request_home() -> Dict[str, Any]:
    return {
        "requestContext": {
            "elb": {
                "targetGroupArn": "arn:aws:elasticloadbalancing:eu-west-2:123456789012:targetgroup/target-group-x/123456789012"
            }
        },
        "httpMethod": "GET",
        "path": "/",
        "queryStringParameters": {},
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.5",
            "host": "test.gds-cyber-security.digital",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "x-forwarded-for": "81.104.91.14",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "body": "",
        "isBase64Encoded": True,
    }
