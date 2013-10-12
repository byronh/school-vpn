#!/usr/bin/env python
import socket
import threading

class VPNServer(threading.Thread):
    def __init__(self, port, shared_secret):
        super(VPNServer, self).__init__()
        self.daemon = True

        self.port = port
        self.shared_secret = shared_secret

        self.running = True
        self.message_received_callbacks = []

        self.client_connection = None
        self.session_key = None

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))

        self.socket.listen(1)

        while self.running:
            self.client_connection, addr = self.socket.accept()

            if self.authenticate_client():
                print "Authenticated sucessfully"
                self.handle_client()
            else:
                try:
                    conn.close()
                except:
                    pass

    def authenticate_client(self):
        client_nonce = self.client_connection.recv(1024)
        challenge = self.generate_challenge(client_nonce)
        nonce = self.generate_nonce()

        self.client_connection.sendall("{}\n{}".format(nonce, challenge))

        challenge_response = self.client_connection.recv(1024)

        print "Received challenge response:\n{}".format(challenge_response)

        if not challenge_response:
            return False

        return self.validate_challenge_response(challenge_response, nonce)

    def generate_nonce(self):
        return 1

    def generate_challenge(self, client_nonce):
        server_host, server_port = self.client_connection.getsockname()
        challenge = "{}\n{}\n{}".format(
                server_host, client_nonce, self.shared_secret)

        # TODO: encrypt challenge

        return challenge

    def validate_challenge_response(self, challenge_response, original_nonce):
        # TODO: decrypt challenge_response

        client_host, nonce, session_key, shared_secret = challenge_response.split("\n")
        nonce = int(nonce)

        connected_client_host, connected_client_port = self.client_connection.getpeername()

        if client_host == connected_client_host and nonce == original_nonce and shared_secret == self.shared_secret:
            self.session_key = session_key
            return True

        return False

    def handle_client(self):
        while self.running:
            encrypted_message = self.client_connection.recv(1024)

            if not encrypted_message:
                return

            # TODO: decrypt message
            plaintext_message = encrypted_message

            for callback in self.message_received_callbacks:
                callback(encrypted_message, plaintext_message)

    def send(self, message):
        if self.client_connection and self.session_key:
            # TODO: encrypt message

            self.client_connection.sendall(message)

    def add_message_received_callback(self, function):
        self.message_received_callbacks.append(function)

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
