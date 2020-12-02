from typing import Any, Callable, Dict, List, Union, Optional

Function = Callable[..., Any]

import json
import re
from functools import wraps

from flask import *
from jsonlogger import LOG  # type: ignore

from .alb import alb_get_user_info
from werkzeug.wrappers import Response as WerkzeugResponse
from flask.wrappers import Response as FlaskWrapperResponse

FlaskResponse = Union[Response, WerkzeugResponse, FlaskWrapperResponse]

STATIC_SITE_ROOT = None
ACCESS_CONTROLS = None
DEFAULT_ACCESS: Dict[str, Any] = {"pages": []}


def set_static_site_root(root: str):
    global STATIC_SITE_ROOT
    STATIC_SITE_ROOT = root


class AccessDeniedException(Exception):
    """
    Raised if access requirements are not met

    Attributes:
        message -- human readable reason for denying access
        request_path -- the denied path requested by the user
    """

    def __init__(self, message: str = "Access denied", request_path: str = "") -> None:
        self.message = message
        self.request_path = request_path
        super(Exception, self).__init__(self.message)


def add_credentials_to_session(app: Flask):
    """
    Retrieve the login credentials from the ALB
    """

    def decorator(route_function: Function) -> Function:
        @wraps(route_function)
        def decorated_function(*args, **kwargs) -> Response:
            app.logger.debug("Add credentials to session")
            if app.config.get("ENV", "debug") == "production":
                try:
                    user_info = alb_get_user_info(
                        request.headers["X-Amzn-Oidc-Data"],
                        verify=app.config.get("verify_oidc", True),
                    )
                    session.new = True
                    session["production_session"] = True
                    session["user_info"] = user_info
                except Exception as error:
                    app.logger.error(error)
                    session.clear()

            else:
                session.new = True
                session["auth_debug"] = True

            response = route_function(*args, **kwargs)
            return response

        return decorated_function

    return decorator


def get_access_file() -> str:
    """
    The static site should contain this JSON file
    alongside the root of the content.
    Requests for his file are refused with a 403.
    """
    return f"{STATIC_SITE_ROOT}access-control.json"


def get_access_controls() -> Dict[str, Any]:
    """
    Parse the access control JSON file

    Load from file once into global var
    and re-use
    """
    global ACCESS_CONTROLS

    if not ACCESS_CONTROLS:
        access_file = get_access_file()
        try:
            with open(access_file, "r") as control_file:
                controls = json.loads(control_file.read())
                controls["access_file"] = access_file
            ACCESS_CONTROLS = controls
        except FileNotFoundError:
            ACCESS_CONTROLS = DEFAULT_ACCESS
        LOG.debug(controls)

    return ACCESS_CONTROLS


def check_role_requirement(
    requirement: Dict[str, Union[str, List[str]]], roles: List[str]
) -> bool:
    """
    Check user roles meets requirement

    A requirement looks like:
    {
        "type": "all|any"
        "roles: ["role_A", "role_B"]
    }
    """
    allow = False
    if requirement["type"] == "all":
        # require user has all the roles specified
        required_set = set(requirement["roles"])
        has_set = set(roles)
        allow = required_set.issubset(has_set)
    elif requirement["type"] == "any":
        # require user has any one of specified roles
        required_set = set(requirement["roles"])
        has_set = set(roles)
        allow = any(role in has_set for role in required_set)
    return allow


def check_access(
    path: str, user: Optional[Dict[str, Union[str, List[str]]]]
) -> None:
    """
    Check request against defined access restrictions

    Assumes get_access_controls returns a parsed JSON
    file detailing paths and access restrictions

    Assumes the user is a dictionary containing a
    roles key with a list of the user's roles

    If logged out the user is None
    """
    if path.endswith("/") or len(path) == 0:
        path = f"{path}index.html"

    LOG.debug(f"Invoke check_access for path: {path}")
    logged_in = user is not None
    controls = get_access_controls()
    allow = True
    found = False
    # Check for content access restrictions
    for auth_path, settings in controls["paths"].items():
        if path.startswith(auth_path):
            found = True
            access_message = settings.get("message", "You need to authenticate.")
            LOG.debug(f"Authed path: {path}")
            if not logged_in:
                allow = settings.get("open_access", False)
                LOG.debug("Access restricted by login status")
            else:
                # Only check roles if auth required and logged in
                if "role_requirements" in settings:
                    for requirement in settings["role_requirements"]:
                        # This mypy errors because user is optional
                        # The none case is handled by the if not logged_in
                        allow = check_role_requirement(
                            requirement, user.get("roles", [])  # type: ignore
                        )

                LOG.debug(f"RBAC status: {allow}")

    if not found:
        allow = logged_in
        access_message = "You need to authenticate."
        LOG.debug("Path not found in config - assuming authentication required")
    if not allow:
        raise AccessDeniedException(request_path=path, message=access_message)


def authorize_or_redirect(app: Flask, denied_route: str = "/access-denied") -> Function:
    """
    Decorator for flask routes to authorize content

    """

    def decorator(route_function: Function) -> Function:
        @wraps(route_function)
        def decorated_function(*args, **kwargs) -> Response:
            path = request.path
            app.logger.debug(f"URL: {path}")

            try:
                check_access(path, session.get("user_info"))
                response = route_function(*args, **kwargs)
            except AccessDeniedException as error:
                session["access_denied_message"] = error.message
                session["request_path"] = path
                response = redirect(denied_route, 302)

            return response

        return decorated_function

    return decorator


def authorize_or_errorhandler(app: Flask) -> Function:
    """
    Decorator for flask routes to authorize content

    On failure the exception is raised and not caught

    This will only work if flask is set to handle
    the exception

    @app.errorhandler(auth.AccessDeniedException)
    def server_access_denied(error):
        return render_template("error.html", error=error), 403
    """

    def decorator(route_function: Function) -> Function:
        @wraps(route_function)
        def decorated_function(*args, **kwargs) -> Response:
            path = request.path
            app.logger.debug(f"URL: {path}")

            check_access(path, session.get("user_info"))
            response = route_function(*args, **kwargs)
            return response

        return decorated_function

    return decorator


def authorize_static(app: Flask) -> Function:
    """Decorator for flask routes to authorize content

    Permissions are based on settings in the parent
    site access-control.json
    """

    def decorator(route_function: Function) -> Function:
        @wraps(route_function)
        def decorated_function(*args, **kwargs) -> Response:
            response = route_function(*args, **kwargs)
            path = request.path

            app.logger.debug(f"URL: {path}")

            # Don't access control asset files
            ext = path.split(".").pop()
            passthru = ext in ["ico", "css", "js", "png", "woff", "woff2"]
            if passthru:
                # remove leading slash to avoid // in path
                path = re.sub("^\/", "", path)
                response = send_from_directory(STATIC_SITE_ROOT, path)

            # Always refuse the access control settings
            if path.endswith("access-control.json"):
                passthru = True
                response = redirect("/", code=302)

            # Otherwise treat as an access controlled content page
            if not passthru:
                # Insert login status component
                content = response.get_data().decode("utf8")
                content = insert_login_component(content, app.config["auth_mode"])

                try:
                    check_access(path, session.get("user_info"))
                except AccessDeniedException as error:
                    access_message = error.message
                    content = insert_denied_component(
                        content, path, access_message, app.config["auth_mode"]
                    )
                    response.headers[
                        "Cache-Control"
                    ] = "no-cache, no-store, must-revalidate"

                response.set_data(content.encode("utf8"))
                response.headers["Content-type"] = "text/html"
            return response

        return decorated_function

    return decorator


def insert_login_component(content: str, auth_mode: str) -> str:
    """
    Show login status

    Adds a login status component in the nav menu
    """
    nav_end = re.compile("\<\/nav\>")
    login_content = render_template("login.html", session=session, auth_mode=auth_mode)
    content = nav_end.sub(f"{login_content}</nav>", content, 1)
    return content


def insert_denied_component(
    content: str, authorised_path: str, access_message: str, auth_mode: str
) -> str:
    """
    Render access denied page

    Replaces the main element content with the
    rendered denied template
    """
    denied_content = render_template(
        "denied.html",
        session=session,
        authorised_path=authorised_path,
        access_message=access_message,
        auth_mode=auth_mode,
    )
    try:
        main_start = content.index("<main")
        main_close = content.index("</main>") + 7
        content = content[0:main_start] + denied_content + content[main_close:]
        # add requested path to session to enable
        # redirect post login
        session["request_path"] = authorised_path
    except ValueError:
        LOG.debug(f"Main tag not found in content for: {authorised_path}")
    return content


def get_static_file_content(path: str) -> Union[str, bytes]:
    """
    Get the file content from a path in the static site

    This function dynamically handles the situation that some static
    files are text (html/css/js) and some are binary assets (png,woff)
    """
    LOG.debug(f"Invoke get_static_site_content for path: {path}")
    try:
        with open(f"{STATIC_SITE_ROOT}{path}", "r") as content_file:
            content = content_file.read()
    except UnicodeDecodeError:
        with open(f"{STATIC_SITE_ROOT}{path}", "rb") as binary_file:
            content = binary_file.read()  # type: ignore
    return content


def make_default_response(path: str) -> FlaskResponse:
    """
    This replaces calls to send_from_directory

    send_from_directory uses passthru mode which
    disables editing of the response content
    """
    if path.endswith("/") or len(path) == 0:
        path = f"{path}index.html"

    LOG.debug(f"Invoke make_default_response for path: {path}")

    content = get_static_file_content(path)
    response = make_response(content)
    return response
