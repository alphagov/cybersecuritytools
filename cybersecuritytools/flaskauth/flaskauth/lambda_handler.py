import serverless_wsgi


from .static_site_wrapper_app import app


def lambda_handler(event, context):
    """
    Lambda handler entry point
    """
    return serverless_wsgi.handle_request(app, event, context)
