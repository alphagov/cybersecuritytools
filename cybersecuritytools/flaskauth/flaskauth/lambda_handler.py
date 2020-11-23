import os
import serverless_wsgi

from .static_site_wrapper_app import app


def lambda_handler(event, context):
    """
    Lambda handler entry point
    """
    app.secret_key = os.getenv("SECRET_KEY", "FALSE")
    return serverless_wsgi.handle_request(app, event, context)
