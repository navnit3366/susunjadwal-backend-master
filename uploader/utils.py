import os
import json

from flask import (
    current_app as app,
    redirect,
    request,
    url_for
)

from app.jwt_utils import decode_token, encode_token
from sso.utils import get_cas_client


def get_scheme():
    if request.is_secure or app.config["SSO_UI_FORCE_HTTPS"]:
        return "https"

    return "http"


def url_for_custom(*args, **kwargs):
    scheme = get_scheme()
    return url_for(*args, **kwargs, _scheme=scheme, _external=True)


def get_sso_login_url():
    service_url = url_for_custom("router_uploader.auth")
    client = get_cas_client(service_url=service_url)
    login_url = client.get_login_url()
    return login_url


def get_sso_logout_url():
    redirect_url = url_for_custom("router_uploader.login")
    client = get_cas_client()
    logout_url = client.get_logout_url(redirect_url=redirect_url)

    return logout_url


def generate_token(sso_profile):
    token = encode_token({
        "username": sso_profile["username"],
        "npm": sso_profile["attributes"]["npm"],
        "kd_org": sso_profile["attributes"]["kd_org"]
    })
    return token


def check_uploader(npm):
    path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(path, "whitelist.json")

    with open(filename) as f:
        as_json = json.loads(f.read())

    return as_json.get(npm)
