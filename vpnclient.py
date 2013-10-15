#!/usr/bin/env python
try:
    import cPickle as pickle
except:
    import pickle
import select
import socket

from vpn import VPN

class VPNClient(VPN):
    def __init__(self, host, port, shared_secret):
        super(VPNClient, self).__init__(port, shared_secret)
        self.host = host

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        challenge_response = None
        nonce = self.generate_nonce()

        while self.running:
            readable, writable, errored = select.select([], [self.socket], [])
            
            if writable:
                self.socket.sendall(pickle.dumps(nonce))
                break

        while self.running:
            readable, writable, errored = select.select([self.socket], [], [])

            if readable:
                response = self.socket.recv(1024)

                server_nonce, challenge = pickle.loads(response)

                print "Received challenge:\n{}".format(challenge)

                challenge_response = self.generate_challenge_response(challenge, nonce, server_nonce)

                if not challenge_response:
                    self.socket.close()
                    return

                break

        while self.running:
            readable, writable, errored = select.select([], [self.socket], [])
            
            if writable:
                self.socket.sendall(challenge_response)
                break

        print "Authenticated successfully"

        self.handle_callbacks(self.connected_callbacks, self.socket)

        self.receive_messages()

        self.handle_callbacks(self.disconnected_callbacks, self.socket)

    def generate_challenge_response(self, challenge, original_nonce, server_nonce):
        # TODO: decrypt challenge

        server_host, nonce, shared_secret = pickle.loads(challenge)
        connected_server_host, connected_server_port = self.socket.getpeername()

        if server_host == connected_server_host and nonce == original_nonce and shared_secret == self.shared_secret:
            self.session_key = self.generate_session_key()
            client_host, client_port = self.socket.getsockname()
            challenge_response = pickle.dumps(
                (client_host, server_nonce, self.session_key, self.shared_secret))

            # TODO: encrypt challenge_response

            return challenge_response

        return False

    def generate_session_key(self):
        return "session key"

if __name__ == "__main__":
    def received_callback(encrypted_message, plaintext_message):
        print "RECEIVED: {}".format(encrypted_message)
        print "DECRYPTED TO: {}".format(plaintext_message)

    client = VPNClient("localhost", 6321, "shared_secret")
    client.add_message_received_callback(received_callback)
    client.start()

    while True:
        message = raw_input(">>")
        client.send(message)
