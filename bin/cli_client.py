from dropbox import client, auth

def login_and_authorize(authorize_url):
    """
    A simple little prompt telling you 
    to go to the given URL and authorize.
    """
    print "AUTHORIZING", authorize_url
    print "GO THERE AND HIT ENTER AFTER APPROVING..."
    raw_input()
    return

# load the configuration file and make an authenticator
config = auth.Authenticator.load_config("config/testing.ini")
dba = auth.Authenticator(config)

# grab the request token
print "GETTING a request token."
token = dba.obtain_request_token()

# make the user log in and authorize this token
print "LOGGING INTO Dropbox to authorize this token."
login_and_authorize(dba.build_authorize_url(token))

print "You should be authorized."

# now use the authorized token to grab an access token
access_token = dba.obtain_access_token(token, config['verifier'])

# and finally make a dropbox client to work with
db_client = client.DropboxClient(config['server'],
             config['content_server'], config['port'], dba, access_token)

# big ugly loop, obviously you want to do something more than just this
while True:
    print "> ",
    command = raw_input()

    if command:
        command = command.strip()
        if command == "put":
            print "FILE:"
            inf = raw_input()
            print "TO PATH:"
            topath = raw_input()
            f = open(inf.strip())
            resp = db_client.put_file("sandbox", topath.strip(), f)
            f.close()
            print resp

        elif command == "get":
            print "FILE:"
            path = raw_input()
            resp = db_client.get_file("sandbox", path.strip())
            print resp.read()

        elif command == "mkdir":
            print "PATH:",
            path = raw_input()
            resp = db_client.file_create_folder("sandbox", path)
            print "STATUS:", resp.status
            print "INFO:", resp.body

        elif command == "cp":
            print "FROM PATH:",
            from_path = raw_input()
            print "TO PATH:",
            to_path = raw_input()

            resp = db_client.file_copy("sandbox", from_path, to_path)
            print "STATUS", resp.status
            print "INFO", resp.body

        elif command == "mv":
            print "FROM PATH:",
            from_path = raw_input()
            print "TO PATH:",
            to_path = raw_input()

            resp = db_client.file_move("sandbox", from_path, to_path)
            print "STATUS", resp.status
            print "INFO", resp.body

        elif command == "rm":
            print "PATH:",
            path = raw_input()
            resp = db_client.file_delete("sandbox", path)
            print "STATUS", resp.status
            print "INFO", resp.body

        elif command == "info":
            resp = db_client.account_info()
            print "STATUS:", resp.status
            print "INFO:", resp.data

        elif command == "ls":
            print "PATH:",
            path = raw_input()
            resp = db_client.metadata("sandbox", path)
            print "STATUS:", resp.status
            print "INFO:", resp.data

        else:
            print "Invalid command."

