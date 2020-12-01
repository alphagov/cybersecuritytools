from typing import Any, Dict

import serverless_wsgi

from .static_site_wrapper_app import app


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Lambda handler entry point
    """
    return serverless_wsgi.handle_request(app, event, context)
