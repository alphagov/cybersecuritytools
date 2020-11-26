import os

from flask import *
from jsonlogger import LOG

from .auth import (
    add_credentials_to_session,
    authorize_static,
    make_default_response,
    set_static_site_root
)
from .config import load_ssm_parameters
from .oidc_client import (
    set_oidc_config,
    get_authorization_url,
    get_authorization_response,
    get_userinfo,
    get_logout_redirect
)

templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
LOG.debug(f"Template folder: {templates}")

app = Flask(__name__, template_folder=templates)
app.logger = LOG
load_ssm_parameters(app)
set_static_site_root(os.environ.get("STATIC_ROOT", ""))
app.config["auth_mode"] = os.environ.get("AUTH_MODE", "flask")
LOG.debug(app.config.keys())

if app.config["auth_mode"] == "flask":
    set_oidc_config(
        endpoint=app.config.get("oidc_root_endpoint"),
        client_id=app.config.get("oidc_client_id"),
        client_secret=app.config.get("oidc_client_secret")
    )


@app.route("/auth")
@app.route("/oauth2/idpresponse")
@add_credentials_to_session(app)
def handle_auth():
    """
    Handles request post ALB authentication
    """
    LOG.debug("Handle auth")
    if "request_path" in session:
        redirect_path = session["request_path"]
        del session["request_path"]
    else:
        redirect_path = "/"
    return redirect(redirect_path, code=302)


@app.route('/login')
def login():
    redirect_to = url_for("/oidc-callback")
    session["login_redirect"] = redirect_to
    auth_url = get_authorization_url(redirect_to)
    LOG.debug(auth_url)
    response = redirect(auth_url)
    return response


@app.route('/oidc-callback')
def auth_callback():
    LOG.debug(vars(request))
    auth_response = get_authorization_response()

    LOG.debug("### auth response ###")
    LOG.debug(vars(auth_response))
    session['user_info'] = get_userinfo(auth_response, session["login_redirect"])
    del (session["login_redirect"])

    if "request_path" in session:
        redirect_path = session["request_path"]
        del(session["request_path"])
    else:
        redirect_path = "/"
    response = redirect(redirect_path)
    return response


@app.route('/logout')
def logout():
    response = get_logout_redirect(request.host_url)
    return response



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