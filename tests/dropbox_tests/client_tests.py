from nose.tools import *
from dropbox import client, rest, auth


config = auth.Authenticator.load_config("config/testing.ini")
dba = auth.Authenticator(config)
access_token = dba.obtain_trusted_access_token(config['testing_user'], config['testing_password'])
db_client = client.DropboxClient(config['server'], config['content_server'], config['port'], dba, access_token)
root = config['root']

CALLBACK_URL = 'http://printer.example.com/request_token_ready'
RESOURCE_URL = 'http://' + config['server'] + '/0/oauth/echo'

def assert_all_in(in_list, all_list):
    assert all(item in in_list for item in all_list), "expected all items in %s to be found in %s" % (all_list, in_list)

def test_delete():
    db_client.file_delete(root, "/tohere")
    return db_client

def test_put_file():
    f = open("tests/dropbox_tests/client_tests.py")
    resp = db_client.put_file(root, "/", f)
    assert resp
    assert_equal(resp.status, 200)

    return db_client

def test_get_file():
    db_client = test_put_file()
    resp = db_client.get_file(root, "/client_tests.py")
    assert_equal(resp.status, 200)
    assert len(resp.read()) > 100

def test_account_info():
    db_client = test_delete()
    resp = db_client.account_info()
    assert resp

    assert_equal(resp.status, 200)
    assert_all_in(resp.data.keys(), [u'country', u'display_name', u'uid', u'quota_info'])


def test_fileops():
    db_client = test_delete()
    test_put_file()

    resp = db_client.file_create_folder(root, "/tohere")
    assert_equal(resp.status, 200)
    assert_all_in(resp.data.keys(), [u'thumb_exists', u'bytes', u'modified', u'path',
                                     u'is_dir', u'size', u'root', u'icon'])

    resp = db_client.file_copy(root, "/client_tests.py", "/tohere/client_tests.py")
    print resp.headers
    assert_equal(resp.status, 200)
    assert_all_in(resp.data.keys(), [u'thumb_exists', u'bytes', u'modified',
                                     u'path', u'is_dir', u'size', u'root',
                                     u'mime_type', u'icon'])

    resp = db_client.file_move(root, "/tohere/client_tests.py",
                                  "/tohere/client_tests.py.temp")
    assert_equal(resp.status, 200)

    resp = db_client.file_delete(root, "/tohere/client_tests.py.temp")
    assert_equal(resp.status, 200)
    assert_all_in(resp.data.keys(), [u'is_deleted', u'thumb_exists', u'bytes', u'modified',
                                     u'path', u'is_dir', u'size', u'root', u'mime_type', u'icon'])

def test_metadata():
    db_client = test_delete()
    resp = db_client.metadata(root, "/tohere")
    assert resp
    assert_equal(resp.status, 200)
    assert_all_in(resp.data.keys(), [u'is_deleted', u'thumb_exists',
                                     u'bytes', u'modified', u'path', u'is_dir',
                                     u'size', u'root', u'hash', u'contents', u'icon'])
def test_links():
    db_client = test_put_file()
    url = db_client.links(root, "/client_tests.py")
    assert_equal(url, "http://" + config['server'] + "/0/links/" + root + "/client_tests.py")

def test_thumbnails():
    db_client.file_delete(root, "/sample_photo.jpg")

    f = open("tests/sample_photo.jpg", "rb")
    resp = db_client.put_file(root, "/", f)
    assert_equal(resp.status, 200)

    resp = db_client.get_file(root, "/sample_photo.jpg")
    body = resp.read()
    assert_equal(resp.status, 200)
    assert len(body) > 0

    resp = db_client.thumbnail(root, "/sample_photo.jpg", size='large')
    thumb = resp.read()
    assert_equal(resp.status, 200)
    assert len(body) > len(thumb)

def test_account():
    """
    This is an example of how you might test the account system, but don't do
    this in real life because it'll polute Dropbox with thousands of useless
    accounts.  We track who's doing this and will block you if we think you're
    abusing it.
    """
    """
    import time
    user_id = str(int(time.time()))
    email = 'api-test-' + user_id + '@tester.com'
    password = 'testing'
    fname, lname = "Api", "Test"
    resp = db_client.account(email, password, fname, lname)
    assert_equal(resp.status, 200) 

    resp = db_client.account(email, password, fname, lname)
    assert_equal(resp.status, 400) 

    config = auth.Authenticator.load_config("config/testing.ini")
    dba = auth.Authenticator(config)
    access_token = dba.obtain_trusted_access_token(email, 'testing')
    cl = client.DropboxClient(config['server'], config['content_server'], config['port'], dba, access_token)
    resp = cl.account_info()
    assert_equal(resp.data['display_name'], fname + " " + lname)
    """
