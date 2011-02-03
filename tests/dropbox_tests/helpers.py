from mechanize import Browser, FormNotFoundError

def login_and_authorize(authorize_url, config):
    print "AUTHORIZING", authorize_url

    br = Browser()
    br.set_debug_redirects(True)
    br.open(authorize_url)
    print "FIRST PAGE", br.title(), br.geturl()
    br.select_form(nr=1)
    br['login_email'] = config['testing_user']
    br['login_password'] = config['testing_password']

    resp = br.submit()
    print "RESULT PAGE TITLE", br.title()
    print "RESULT URL", resp.geturl()

    assert br.viewing_html(), "Looks like it busted."

    try:
        br.select_form(nr=1)
        br.submit()
        assert br.viewing_html(), "Looks like it busted."
        assert "API Request Authorized" in br.title(), "Title Is Wrong (bad email/password?): %r at %r" % (br.title(), br.geturl())
    except FormNotFoundError:
        print "Looks like we're blessed."


