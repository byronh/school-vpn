import select
import threading

from Crypto import Random
from Crypto.Cipher import AES


class VPN(threading.Thread):
    def __init__(self, port, shared_secret):
        super(VPN, self).__init__()
        self.daemon = True

        self.port = port
        self.shared_secret = shared_secret

        self.running = True
        self.message_received_callbacks = []
        self.message_sent_callbacks = []
        self.connected_callbacks = []
        self.disconnected_callbacks = []

        self.session_key = None
        self.session_iv = None
        self.socket = None

        if len(shared_secret) > 32:
            shared_secret = shared_secret[:32]

        while len(shared_secret) not in [16, 24, 32]:
            shared_secret += '\x00'

        self.authentication_crypto = AES.new(shared_secret, AES.MODE_ECB)
        self.session_crypto = None

    def generate_nonce(self):
        # generate a 32-bit nonce
        return Random.get_random_bytes(4)

    def auth_encrypt(self, message):
        padded_message = self.pad_message(message)
        return self.authentication_crypto.encrypt(padded_message)

    def auth_decrypt(self, message):
        padded_message = self.pad_message(message)
        return self.authentication_crypto.decrypt(padded_message)

    def session_encrypt(self, message):
        padded_message = self.pad_message(message)
        return self.session_crypto.encrypt(padded_message)

    def session_decrypt(self, message):
        padded_message = self.pad_message(message)
        return self.session_crypto.decrypt(padded_message)

    def send(self, message):
        if self.socket is None or self.session_crypto is None:
            return

        while self.running:
            readable, writable, errored = select.select([], [self.socket], [])

            if writable:
                encrypted_message = self.session_encrypt(message)

                self.socket.sendall(encrypted_message)

                self.handle_callbacks(self.message_sent_callbacks, message, encrypted_message)

                break

    def pad_message(self, message, multiple=16):
        while len(message) % 16 != 0:
            message += '\x00'

        return message

    def receive_messages(self):
        if self.session_crypto is None:
            return

        while self.running:
            readable, writable, errored = select.select([self.socket], [], [])

            if readable:
                encrypted_message = self.socket.recv(1024)

                if not encrypted_message:
                    # the client disconnected
                    return

                plaintext_message = self.session_decrypt(encrypted_message)

                self.handle_callbacks(self.message_received_callbacks, encrypted_message, plaintext_message)

    def handle_callbacks(self, callbacks_list, *args):
        for callback, extra_args in callbacks_list:
            callback(*(args + extra_args))

    def add_message_received_callback(self, function, *extra_args):
        self.message_received_callbacks.append((function, extra_args))

    def add_message_sent_callback(self, function, *extra_args):
        self.message_sent_callbacks.append((function, extra_args))

    def add_connected_callback(self, function, *extra_args):
        self.connected_callbacks.append((function, extra_args))

    def add_disconnected_callback(self, function, *extra_args):
        self.disconnected_callbacks.append((function, extra_args))

    def kill(self, wait=False):
        self.running = False

        if wait:
            self.join()
