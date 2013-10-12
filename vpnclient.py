#!/usr/bin/env python
import socket
import threading

class VPNClient(threading.Thread):
    def __init__(self, server_host, server_port, shared_secret):
        super(VPNClient, self).__init__()
        self.daemon = True

        self.server_host = server_host
        self.server_port = server_port
        self.shared_secret = shared_secret

        self.running = True
        self.message_received_callbacks = []

        self.socket = None
        self.session_key = None

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

        nonce = self.generate_nonce()

        self.socket.sendall(str(nonce))

        response = self.socket.recv(1024)

        server_nonce, challenge = response.split("\n", 1)
        server_nonce = int(server_nonce)

        print "Received challenge:\n{}".format(challenge)

        challenge_response = self.generate_challenge_response(challenge, nonce, server_nonce)

        if challenge_response:
            self.socket.sendall(challenge_response)
        else:
            self.socket.close()
            return

        print "Authenticated successfully"

        while self.running:
            encrypted_message = self.socket.recv(1024)

            if not encrypted_message:
                continue

            # TODO: decrypt the message
            plaintext_message = encrypted_message

            for callback in self.message_received_callbacks:
                callback(encrypted_message, plaintext_message)

    def generate_nonce(self):
        return 0

    def generate_challenge_response(self, challenge, original_nonce, server_nonce):
        # TODO: decrypt challenge

        server_host, nonce, shared_secret = challenge.split("\n")
        nonce = int(nonce)
        connected_server_host, connected_server_port = self.socket.getpeername()

        if server_host == connected_server_host and nonce == original_nonce and shared_secret == self.shared_secret:
            self.session_key = self.generate_session_key()
            client_host, client_port = self.socket.getsockname()
            challenge_response = "{}\n{}\n{}\n{}".format(
                    client_host, server_nonce, self.session_key, self.shared_secret)

            # TODO: encrypt challenge_response

            return challenge_response

        return False

    def generate_session_key(self):
        return "session key"

    def send(self, message):
        if self.socket and self.session_key:
            # TODO: encrypt message

            self.socket.sendall(message)

    def add_message_received_callback(self, function):
        self.message_received_callbacks.append(function)

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
