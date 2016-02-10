import datetime
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
        s.send_header("Access-Control-Allow-Origin", "*")
        s.send_header("Content-type", "text/html")
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
            cc = s.GetDatabaseCursor()

            try:
                c.execute("SELECT Time, Channel, Message FROM chatdata WHERE user=? ORDER BY Time ASC",(user.lower(),))
                
            except Exception as e:
                print("Exception when quering")
                print(user.lower(), type(user.lower), type(user))
                

            cc.execute("SELECT Time, Channel FROM bans WHERE user=? ORDER BY Time ASC",(user.lower(),))

            userData = {"username":user, "banned":0, "messages":[]}
            banData = cc.fetchall()

            for message in c.fetchall():
                try:
                    userData["messages"].append({"type":"message", "time":message[0], "channel":message[1], "message":message[2]})
                except Exception as E:
                    print("Exeption when making dictionary")
                    print(E, len(message), message)

            userData["banned"] = len(banData)
            for ban in banData:
                userData["messages"].append({"type":"ban", "time":ban[0], "channel":ban[1]})

            userData["messages"].sort(key=lambda x:x["time"])


            c.close()
            cc.close()

            if len(userData["messages"]) != 0:
                s.send_response(200)
                s.send_header("Access-Control-Allow-Origin", "*")
                s.send_header("Content-type", "text/json")
                s.send_header("Connection", "close")
                s.end_headers()
                # Send User Message data
                s.wfile.write(B(json.dumps(userData)))

            else: #404
                s.send_response(404)
                s.send_header("Access-Control-Allow-Origin", "*")
                s.send_header("Content-type", "text/json")
                s.end_headers()
                #Send User not found data
                #s.wfile.write(B(json.dumps()))

            return


        s.fourohfourResponse()

class WebServer(object):

    def __init__(self):
        print("Created Webserver Object at {}".format(datetime.datetime.now()))
        self.ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ctx.load_cert_chain(certfile="config/server.crt", keyfile="config/server.key")
        self.httpd = http.HTTPServer(("0.0.0.0", 8443), SimpleDBResponder)
        self.httpd.socket = self.ctx.wrap_socket(self.httpd.socket, server_side=True)
        #self.link = socket.socket()
        #self.link.bind(("0.0.0.0", 4443))

    def RespondRequest(self):
        self.httpd.serve_forever()

    def MainLoop(self, fork=True):
        print("Starting webserver at {} serving on {}".format(datetime.datetime.now(), self.httpd.server_address))
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
    Database = SQL.connect("config/bot.db")
    SimpleDBResponder.DATABASETMPLINK = Database
    a = WebServer()
    a.defaultCursor = Database.cursor()
    a.MainLoop(False)
