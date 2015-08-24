# Echo server program
import socket
import codecs
import threading

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 6667              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()

def read_from():

    print('Connected by', addr)
    while True:
        data = conn.recv(1024)
        if not data: break
        print("->"+codecs.decode(data, "UTF-8").strip("\r\n"))
        #conn.sendall(data)
    conn.close()

def send_file(filename):
    with open(filename, encoding="UTF-8") as fin:
        for i in fin:
            # print(i)
            conn.sendall(codecs.encode(i.strip()+"\r\n","UTF-8"))
        
t = threading.Thread(target=read_from)
t.daemon =True
t.start()

inp = input(">>")
while inp != "QUIT":
    print(inp)
    if inp[0] == '$' and inp[-1] == "!":
        if inp[1:-1] == "send_file":
            send_file("scrape.log")
    else:
        conn.sendall(codecs.encode(inp+"\r\n", "UTF-8"))
    
    inp = input(">>")

