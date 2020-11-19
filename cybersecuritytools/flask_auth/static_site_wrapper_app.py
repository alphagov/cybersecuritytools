import os

import auth
from flask import *
from oidc import (
    AUTHMACHINE_API_TOKEN,
    AUTHMACHINE_URL,
    AuthMachineClient,
    no_ssl_verification,
)

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET", "flask-secret")
auth.set_static_site_root(os.environ.get("STATIC_CONTENT", ""))


@app.route("/login")
def login():
    with no_ssl_verification():
        client = AuthMachineClient()
        auth_url = client.get_authorization_url()
        print(auth_url)
        response = redirect(auth_url)
    return response


@app.route("/oidc-callback")
def auth_callback():
    with no_ssl_verification():
        print(vars(request))
        client = AuthMachineClient()
        aresp = client.get_authorization_response()
        print("### auth response ###")
        print(vars(aresp))
        session["user_info"] = client.get_userinfo(aresp)
        if "request_path" in session:
            redirect_path = session["request_path"]
            del session["request_path"]
        else:
            redirect_path = "/"
        response = redirect(redirect_path)
    return response


@app.route("/logout")
def logout():
    global AUTHMACHINE_API_TOKEN
    with no_ssl_verification():
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = "Token %s" % AUTHMACHINE_API_TOKEN
        redirect_url = request.host_url
        logout_url = f"{AUTHMACHINE_URL}protocol/openid-connect/logout?redirect_uri={redirect_url}"

        if "user_info" in session:
            del session["user_info"]

        response = redirect(logout_url)
        print(str(vars(response)))
        AUTHMACHINE_API_TOKEN = None
    return response


@app.route("/auth")
@auth.add_credentials_to_session()
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
@auth.authorize_static(app)
def static_site_page(path=""):
    print("default route")

    # This can't be a send_from_directory because
    # the decorator manipulates the content and
    # flask protects against that happening in
    # send_from_directory passthru mode
    response = auth.make_default_response(path)

    return response
