import socket
import ssl
import threading
import json
import sqlite3 as SQL
import http.server as http

#simple bytes lambda wrapper
B = lambda x: bytes(x, "UTF-8")

class SimpleDBResponder(http.BaseHTTPRequestHandler):
    DATABASETMPLINK = None
    def GetDatabaseCursor(self):
        if self.DATABASETMPLINK:
            return self.DATABASETMPLINK.cursor()

    def fourohfourResponse(s):
        s.send_response(404)
        s.send_header(B("Content-type"), B("text/plain"))
        s.end_headers()
        s.wfile.write(B("<html><head><title>404</title></head>"))
        s.wfile.write(B("<body><p>That Page Does Not Exist</p>"))
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        s.wfile.write(B("<p>You accessed path: %s</p>" % s.path))
        s.wfile.write(B("</body></html>"))

    def do_GET(s):

        if not s.path.startswith("/api/"):
            s.fourohfourResponse()
            return

        try:
            args = s.path.split('?',1)[1].split("&")
        except:
            args = []
        breadcrumbs = s.path.split('?',1)[0].split('/')[1:]

        if breadcrumbs[1] == "users":
            # Get User Argument
            for keyvalue in args:
                # Split only if found the right key
                if keyvalue.startswith("user"):
                    user = keyvalue.split('=')[1]
                    break
            else:
                print("user not found, return none")
                s.fourohfourResponse()
                return

            c = s.GetDatabaseCursor()
            c.execute("SELECT Time, Channel, Message FROM chatdata WHERE user=? ORDER BY Time ASC",(user.lower(),))

            userData = {"username":user, "messages":[]}

            for message in c.fetchall():
                userData["messages"].append({"time":message[0], "channel":message[1], "message":message[2]})

            if len(userData["messages"]) != 0:
                s.send_response(200)
                s.send_header(B("Content-type"), B("text/json"))
                s.send_header(B("Connection"), B("close"))
                s.end_headers()
                # Send User Message data
                s.wfile.write(B(json.dumps(userData)))

            else: #404
                s.send_response(404)
                s.send_header(B("Content-type"), B("text/json"))
                s.end_headers()
                #Send User not found data
                #s.wfile.write(B(json.dumps()))

            return
        s.fourohfourResponse()

class WebServer(object):

    def __init__(self):
        self.ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ctx.load_cert_chain(certfile="server.crt", keyfile="server.key")
        self.httpd = http.HTTPServer(("0.0.0.0", 4443), SimpleDBResponder)
        self.httpd.socket = self.ctx.wrap_socket(self.httpd.socket, server_side=True)
        #self.link = socket.socket()
        #self.link.bind(("0.0.0.0", 4443))

    def RespondRequest(self):
        self.httpd.serve_forever()

    def MainLoop(self, fork=True):
        if fork:

            self.thread_object = threading.Thread(
                target=self.RespondRequest,
                daemon=True
            )

            self.thread_object.start()

            return self.thread_object

        else:
            self.RespondRequest()


if __name__ == '__main__':
    print("starting webserver")
    Database = SQL.connect("bot.db")
    SimpleDBResponder.DATABASETMPLINK = Database
    a = WebServer()
    a.defaultCursor = Database.cursor()
    a.MainLoop(False)

"""
while(True):
    self.link.listen(3)
    conn,addr = self.link.accept()
    connstream = self.ctx.wrap_socket(conn, server_side=True)

    #a = connstream.recv(4096).decode("UTF-8").split("\r\n")
    dataraw = connstream.recv(4096).decode("UTF-8")
    datastream = dataraw.split('\r\n')
    try:
        # Print Receveing message to console
        for line in datastream:
            print(line)

        # Retrive the data request, close the connection on error
        dataRequest = datastream[0].split(' ',2)[1]

        # get user variable from request
        keypairs = dataRequest.split("?",1)[1].split("&")

        for keyvalue in keypairs:
            # Split only if found the right key
            if keyvalue.startswith("user"):
                user = i.split('=')[1]
                break

        print("requested user data:"+user)

        self.defaultCursor.execute()

        userData = {"username":user, "messages":[]}

        for message in self.defaultCursor.fetchall():
            userData["messages"].append({"time":message[0], "channel":message[1], "message":message[2]})

        sendString = ""
        print(len(userData["messages"]))
        if len(userData["messages"]) != 0:
            sendData = json.dumps(userData)
            sendString = "HTTP/1.1 200 OK\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {length}\r\nContent-Type: text/json\r\n\r\n{Body}".format(
                    length=len(sendData),
                    Body=sendData
                )
        else:
            sendString = "HTTP/1.1 404 Not Found\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: 0\r\nContent-Type: text/json\r\n\r\n"

        connstream.sendall(bytes(sendString,"UTF-8"))

    except Exception as E:
        print("main exception")
        print(E)
        print(dataraw)

    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()
        print("closed the server connection")
"""
