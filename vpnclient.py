#!/usr/bin/env python
try:
    import cPickle as pickle
except:
    import pickle
import select
import socket

from Crypto import Random
from Crypto.Cipher import AES

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
        self.setup_auth_crypto(nonce)

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

    def generate_challenge_response(self, encrypted_challenge, original_nonce, server_nonce):
        challenge = self.auth_decrypt(encrypted_challenge)

        server_host, server_port, nonce, shared_secret = pickle.loads(challenge)
        connected_server_host, connected_server_port = self.socket.getpeername()

        if server_host == connected_server_host and server_port == connected_server_port and nonce == original_nonce and shared_secret == self.shared_secret:
            self.session_key = self.generate_session_key()
            self.session_iv = self.generate_iv()
            self.session_crypto = AES.new(self.session_key, AES.MODE_CBC, self.session_iv)
            client_host, client_port = self.socket.getsockname()
            challenge_response = pickle.dumps(
                (client_host, client_port, server_nonce, self.session_key, self.session_iv, self.shared_secret))

            return self.auth_encrypt(challenge_response)

        return False

    def generate_session_key(self):
        return Random.get_random_bytes(32)

    def generate_iv(self):
        return Random.get_random_bytes(16)

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
