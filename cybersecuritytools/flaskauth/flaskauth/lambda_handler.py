import os
import serverless_wsgi

from .config import load_ssm_parameters
from .static_site_wrapper_app import app


def lambda_handler(event, context):
    """
    Lambda handler entry point
    """
    load_ssm_parameters(app)
    app.secret_key = os.getenv("SECRET_KEY", "FALSE")
    return serverless_wsgi.handle_request(app, event, context)
