import select
import threading


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
        self.socket = None

    def generate_nonce(self):
        return 0

    def send(self, message):
        if self.socket is None:
            return

        while self.running:
            readable, writable, errored = select.select([], [self.socket], [])

            if writable and self.session_key:
                # TODO: encrypt message
                encrypted_message = message

                self.socket.sendall(encrypted_message)

                self.handle_callbacks(self.message_sent_callbacks, message, encrypted_message)

                break

    def receive_messages(self):
        while self.running:
            readable, writable, errored = select.select([self.socket], [], [])

            if readable:
                encrypted_message = self.socket.recv(1024)

                if not encrypted_message:
                    # the client disconnected
                    return

                # TODO: decrypt message
                plaintext_message = encrypted_message

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
