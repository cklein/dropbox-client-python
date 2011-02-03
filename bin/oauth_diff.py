from urllib import unquote
import difflib


print "PASTE IN SERVER EXPECTED: \n"
server = raw_input()

print "PASTE IN CLIENT SENT: \n"
client = raw_input()


s_params = [i + "\n" for i in unquote(server).split("&")]
c_params = [i + "\n" for i in unquote(client).split("&")]

print "\n\nSERVER\n------\nCLIENT\n"

diff = difflib.context_diff(s_params, c_params)

print "".join(diff)


