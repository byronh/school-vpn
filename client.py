from twisted.internet import reactor
from twisted.internet import main, protocol, task
from twisted.protocols.basic import LineReceiver


class VPNClientProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.connection_established(self)
    
    def connectionLost(self, reason):
        pass

    def lineReceived(self, line):
        print "Server said:", line
        self.transport.write(line)
        #self.transport.loseConnection()
        #testcommitacomment

class VPNClientFactory(protocol.ClientFactory):

    protocol = VPNClientProtocol

    def startedConnecting(self, connector):
        print "Connecting to server..."

    def clientConnectionFailed(self, connector, reason):
        print "Failed to connect to server."
        # It may be useful to call connector.connect() - this will reconnect (?).
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print "Disconnected from server."
        # It may be useful to call connector.connect() - this will reconnect (?).
        reactor.stop()

    def connection_established(self, client):
        self.client = client
        print "Connected to server."

    def send_message(self, message):
        print "Sending message to server."
        self.client.transport.write(message + "\r\n")

def main():
    # Connect to server
    server = VPNClientFactory()
    reactor.connectTCP("192.110.160.199", 6318, server)
    reactor.run()
    #.send_message("Hello!")

if __name__ == "__main__":
    main()
