#!/usr/bin/env python
try:
    import cPickle as pickle
except:
    import pickle
import select
import socket

from Crypto.Cipher import AES

from vpn import VPN

class VPNServer(VPN):
    def __init__(self, port, shared_secret):
        super(VPNServer, self).__init__(port, shared_secret)
        self.listen_socket = None

    def run(self):
        print "Starting server"
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind(("", self.port))

        self.listen_socket.listen(1)

        while self.running:
            print "Listening for client"
            readable, writable, errored = select.select([self.listen_socket], [], [])

            if readable:
                self.socket, addr = self.listen_socket.accept()

                if self.authenticate_client():
                    self.handle_callbacks(self.connected_callbacks, self.socket)
                    print "Authenticated sucessfully"
                    self.receive_messages()
                else:
                    try:
                        self.socket.close()
                    except:
                        pass
                self.handle_callbacks(self.disconnected_callbacks, self.socket)

                self.socket = None
                self.session_key = None
                self.session_crypto = None

    def authenticate_client(self):
        print "Authenticating client"
        while self.running:
            readable, writable, errored = select.select([self.socket], [], [])

            if readable:
                client_nonce = pickle.loads(self.socket.recv(1024))
                challenge = self.generate_challenge(client_nonce)
                nonce = self.generate_nonce()
                break

        while self.running:
            readable, writable, errored = select.select([], [self.socket], [])

            if writable:
                self.socket.sendall(pickle.dumps((nonce, challenge)))
                break

        while self.running:
            readable, writable, errored = select.select([self.socket], [], [])

            if readable:
                challenge_response = self.socket.recv(1024)

                print "Received challenge response:\n{}".format(challenge_response)

                if not challenge_response:
                    return False

                return self.validate_challenge_response(challenge_response, nonce)
        return False

    def generate_challenge(self, client_nonce):
        server_host, server_port = self.socket.getsockname()
        challenge = pickle.dumps((server_host, client_nonce, self.shared_secret))

        return self.auth_encrypt(challenge)

    def validate_challenge_response(self, encrypted_challenge_response, original_nonce):
        challenge_response = self.auth_decrypt(encrypted_challenge_response)

        client_host, nonce, session_key, session_iv, shared_secret = pickle.loads(challenge_response)

        connected_client_host, connected_client_port = self.socket.getpeername()

        if client_host == connected_client_host and nonce == original_nonce and shared_secret == self.shared_secret:
            self.session_key = session_key
            self.session_iv = session_iv
            self.session_crypto = AES.new(self.session_key, AES.MODE_CBC, self.session_iv)
            return True

        return False

if __name__ == "__main__":
    def received_callback(encrypted_message, plaintext_message):
        print "RECEIVED: {}".format(encrypted_message)
        print "DECRYPTED TO: {}".format(plaintext_message)

    server = VPNServer(6321, "shared_secret")
    server.add_message_received_callback(received_callback)
    server.start()

    while True:
        message = raw_input(">>")
        server.send(message)
