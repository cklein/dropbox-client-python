from nose.tools import *
from dropbox.rest import *



class TestRESTClient(object):
    
    def setup(self):
        self.rc = RESTClient('www.dropbox.com', 80)

    def test_request(self):
        resp = self.rc.request('GET', '/static/images/favicon.ico')
        assert resp
        assert_equal(resp.status, 200)
        assert resp.body
        assert_equal(resp.reason, "OK")


    def test_GET(self):
        resp = self.rc.GET("/static/images/favicon.ico")
        assert_equal(resp.status, 200)
        assert resp.body




