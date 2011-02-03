from nose.tools import *
from dropbox import auth
from helpers import login_and_authorize

CALLBACK_URL = 'http://printer.example.com/request_token_ready'
RESOURCE_URL = 'http://www.dropbox.com/0/oauth/echo'


def test_config():
    config = auth.Authenticator.load_config("config/testing.ini")

    for key in ['server', 'port', 'consumer_key', 'consumer_secret', 'verifier']:
        assert key in config, "Key %s is not set in config/testing.ini." % key

    return config


def test_obtain_request_token():
    config = test_config()

    dba = auth.Authenticator(config)
    token = dba.obtain_request_token()

    assert token
    assert dba.oauth_request

    return token

def test_obtain_access_token():
    config = test_config()
    dba = auth.Authenticator(config)
    req_token = dba.obtain_request_token()
    assert req_token and dba.oauth_request

    authorize_url = dba.build_authorize_url(req_token, callback="http://comback.com/")
    assert "comback" in authorize_url, "Should have the return address in it."

    authorize_url = dba.build_authorize_url(req_token)
    login_and_authorize(authorize_url, config)

    access_token = dba.obtain_access_token(req_token, config['verifier'])

    assert access_token
    assert dba.oauth_request
    assert access_token.key != req_token.key
    return access_token, dba

def test_obtain_trusted_access_token():
    config = auth.Authenticator.load_config("config/testing.ini")
    dba = auth.Authenticator(config)
    token = dba.obtain_trusted_access_token(config['testing_user'], config['testing_password'])
    assert token

def test_build_access_headers():
    token, dba = test_obtain_access_token()

    assert token

    headers, params = dba.build_access_headers("GET", token, RESOURCE_URL, {'image': 'test.png'}, CALLBACK_URL)

    assert headers
    assert params

