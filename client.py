import socket


class Client(object):

    def connect(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def disconnect(self):
        self.sock.close()

    def send(self, message):
        self.sock.sendall(message)
        result = self.sock.recv(1024)
        print "Received response '%s' from server" % result
        return result


if __name__ == "__main__":

    client = Client()
    client.connect("localhost", 6321)

    while True:
        data = raw_input("Enter message: ")
        client.send(data)

    client.disconnect()    