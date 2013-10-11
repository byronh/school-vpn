import socket


class Server(object):

    def start(self, port):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", port))

        print "TCP server listening on port", port
    
    def listen(self):
        self.sock.listen(1)

        conn, addr = self.sock.accept()
        print "Client connection received from", addr

        while True:
            data = conn.recv(1024)

            if not data:
                continue

            result = self.process(data)
            print "Received %s, sending %s" % (data, result)
            conn.sendall(result)

        conn.close()

    def process(self, message):
        return message.upper() #placeholder, do something with the message


if __name__ == "__main__":
    
    server = Server()
    server.start(6321)
    server.listen()
