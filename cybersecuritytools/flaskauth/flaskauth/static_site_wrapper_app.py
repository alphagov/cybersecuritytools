import os

from flask import *
from logger import LOG

from .auth import (
    add_credentials_to_session,
    authorize_static,
    make_default_response,
    set_static_site_root
)

templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
LOG.debug(f"Template folder: {templates}")
app = Flask(__name__, template_folder=templates)
app.logger = LOG
app.secret_key = os.environ.get("APP_SECRET", "flask-secret")
set_static_site_root(os.environ.get("STATIC_ROOT", ""))


@app.route("/auth")
@app.route("/oauth2/idpresponse")
@add_credentials_to_session(app)
def handle_auth():
    """
    Handles request post ALB authentication
    """
    if "request_path" in session:
        redirect_path = session["request_path"]
        del session["request_path"]
    else:
        redirect_path = "/"
    return redirect(redirect_path, code=302)


@app.route("/")
@app.route("/<path:path>")
@authorize_static(app)
def static_site_page(path=""):
    app.logger.debug("default route")

    # This can't be a send_from_directory because
    # the decorator manipulates the content and
    # flask protects against that happening in
    # send_from_directory passthru mode
    response = make_default_response(path)

    return response