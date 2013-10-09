from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver


class VPNServerProtocol(LineReceiver):

    def connectionMade(self):
        self.peer = self.transport.getPeer()
        print "A client has connected to the server.", self.peer
        self.factory.connections.append(self)

    def connectionLost(self, reason):
        print "A client has disconnected from the server.", self.peer
        self.peer = None
        self.factory.connections.remove(self)

    def lineReceived(self, line):
        print "Client said:", line
        self.transport.write(line)


class VPNServerFactory(protocol.ServerFactory):

    protocol = VPNServerProtocol

    def __init__(self):
        self.connections = []

    def startFactory(self):
        print("Server initialized.")

    def stopFactory(self):
        print("Server terminated.")


def main():
    factory = VPNServerFactory()
    reactor.listenTCP(6318, factory)
    reactor.run()

if __name__ == "__main__":
    main()