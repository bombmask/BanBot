import socket
import threading
import json
import sqlite3 as SQL

class WebServer(object):

    def __init__(self):
        self.link = socket.socket()
        self.link.bind(("0.0.0.0", 8080))

    def AddMe(self, ref):
        self.ref = ref
        self.defaultCursor = ref.dbConn.cursor()

    def RespondRequest(self):
        while(True):
            self.link.listen(1)
            conn = self.link.accept()
            a = conn[0].recv(4096).decode("UTF-8").split("\r\n")
            try:
                for i in (a):
                    print(i)

                try:
                    REQUEST = a[0].split(' ')[1]
                except IndexError:
                    print("ERROR!!")
                    print(a[0])

                user = REQUEST.split("?",1)[1].split("&")
                for i in user:
                    if i.startswith("user"):
                        user = i.split('=')[1]

                print("requested user data:"+user)

                self.defaultCursor.execute("SELECT Time, Channel, Message FROM chatdata WHERE user=? ORDER BY Time ASC",(user.lower(),))

                userData = {"username":user, "messages":[]}

                for message in self.defaultCursor.fetchall():
                    userData["messages"].append({"time":message[0], "channel":message[1], "message":message[2]})

                sendString = ""
                print(len(userData["messages"]))
                if len(userData["messages"]) != 0:
                    sendData = json.dumps(userData)
                    sendString = "HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {length}\r\nContent-Type: text/json\r\n\r\n{Body}".format(
                            length=len(sendData),
                            Body=sendData
                        )
                else:
                    sendString = "HTTP/1.1 404 Not Found\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: 0\r\nContent-Type: text/json\r\n\r\n"

                conn[0].sendall(bytes(sendString,"UTF-8"))

            except Exception as E:
                print(E)

            conn[0].close()



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
    a = WebServer()
    a.defaultCursor = Database.cursor()
    a.MainLoop(False)
