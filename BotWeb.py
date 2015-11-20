import socket
import threading
import json
import sqlite3 as SQL

class WebServer(object):

    def __init__(self):
        self.link = socket.socket()
        self.link.bind(("localhost", 80))

    def AddMe(self, ref):
        self.ref = ref

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

                print(REQUEST)

                very_large_file = json.dumps({"content":{"main":{"trash":"====Hello world====\r\n"*500}}})


                conn[0].sendall(
                    bytes(
                        "HTTP/1.1 200 OK\r\nContent-Length: {length}\r\nContent-Type: text/json\r\n\r\n{Body}".format(
                                length=len(very_large_file),
                                Body=very_large_file
                            ),
                        "UTF-8"
                        )
                )
            except Error as E:
                print(E)

            conn[0].close()



    def MainLoop(self, fork=False):
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
    a = WebServer()
    a.MainLoop(False)
