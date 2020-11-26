from urllib.parse import urlencode

from flask import *
from jsonlogger import LOG
from oic import rndstr
from oic.oauth2 import AuthorizationResponse
from oic.oic import Client
from oic.utils.authn.client import ClientSecretBasic, ClientSecretPost

CONFIG = {}


def get_host():
    host = request.host_url
    return host


def set_oidc_config(endpoint, client_id, client_secret, scope="openid profile email roles"):
    CONFIG["endpoint"] = endpoint
    CONFIG["client_id"] = client_id
    CONFIG["client_secret"] = client_secret
    CONFIG["scope"] = scope


def get_client():
    if "client" not in CONFIG:
        client = Client(client_authn_method={
            'client_secret_post': ClientSecretPost,
            'client_secret_basic': ClientSecretBasic
        })
        client.provider_config(CONFIG["endpoint"])
        LOG.debug(CONFIG["endpoint"])
        client.client_id = CONFIG["client_id"]
        client.client_secret = CONFIG["client_secret"]

    CONFIG["client"] = client

    return CONFIG["client"]


def get_authorization_url(redirect_to):
    """
    Get login url
    """
    nonce = rndstr()
    client = get_client()

    args = {
        'client_id': client.client_id,
        'response_type': 'code',
        'scope': CONFIG["scope"],
        'nonce': nonce,
        'redirect_uri': redirect_to,
        'state': 'some-state-which-will-be-returned-unmodified'
    }
    url = client.provider_info['authorization_endpoint'] + '?' + urlencode(args, True)
    return url


def get_access_token(auth_response, redirect_to):
    """
    Get an access token
    """
    client = get_client()
    args = {
        'code': auth_response['code'],
        'client_id': client.client_id,
        'client_secret': client.client_secret,
        'redirect_uri': redirect_to
    }
    response = client.do_access_token_request(
        scope=CONFIG["scope"],
        state=auth_response['state'],
        request_args=args,
        authn_method='client_secret_post')

    LOG.debug("Token response: " + str(response))

    return response


def get_user_roles(token):
    """
    Get roles list from user_info
    """
    token_dict = token.to_dict()
    roles = token_dict["id_token"]["realm_access"]["roles"]
    return roles


def get_userinfo(auth_response):
    """
    Make userinfo request
    """
    client = get_client()
    token = get_access_token(auth_response)
    CONFIG["token"] = token

    roles = get_user_roles(token)

    user_info = client.do_user_info_request(
        state=auth_response['state'],
        authn_method='client_secret_post')
    user_info_dict = user_info.to_dict()
    user_info_dict["roles"] = roles
    return user_info_dict


def get_authorization_response():
    """
    Parse authorization response
    """
    client = get_client()
    authorization_response = client.parse_response(
        AuthorizationResponse,
        info=request.args,
        sformat='dict'
    )
    return authorization_response


def get_logout_redirect(redirect_to):
    headers = {}
    headers['Content-Type'] = 'application/json'
    # I don't think we need an auth header since we're actually
    # redirecting to the site rather than making an API call

    # headers['Authorization'] = 'Token %s' % CONFIG["token"]
    client = get_client()
    args = {
        "redirect_uri": redirect_to
    }
    logout_url = client.provider_info['end_session_endpoint'] + '?' + urlencode(args, True)

    if 'user_info' in session:
        del session['user_info']

    response = redirect(logout_url)
    return response