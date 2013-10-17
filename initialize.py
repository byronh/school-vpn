#!/usr/bin/env python
import binascii

import gtk
import Queue
import socket

from vpnserver import VPNServer
from vpnclient import VPNClient

class ApplicationGUI(object):
    def enter_callback(self, widget, entry):
        entry_text = entry.get_text()
        print "Entry contents: %s\n" % entry_text

    def enter_send_callback(self, widget, entry):
        entry_text = entry.get_text()
        self.vpn.send(entry_text)

    def start_callback(self, widget, host_entry, port_entry, cipher_text_entry):
        self.shared_secret_entry.set_editable(False)
        if widget.get_label() == "Start Server":
            self.vpn = VPNServer(int(port_entry.get_text()), self.shared_secret_entry.get_text())
            self.vpn.add_bind_port_callback(self.bind_port_callback)
        else:
            self.vpn = VPNClient(host_entry.get_text(), int(port_entry.get_text()), self.shared_secret_entry.get_text())
            self.vpn.add_disconnected_callback(self.disconnected_from_server_callback)

        self.vpn.add_message_received_callback(self.message_received_callback)
        self.vpn.add_message_sent_callback(self.message_sent_callback, cipher_text_entry)
        self.vpn.add_shared_secret_callback(self.shared_secret_callback)
        self.vpn.start()

    def stop_vpn(self):
        self.vpn.kill()
        self.shared_secret_entry.set_editable(True)

    def client_connected_callback(self, socket):
        pass

    def client_disconnected_callback(self, socket):
        pass

    def connected_to_server_callback(self, socket):
        pass

    def disconnected_from_server_callback(self, socket):
        self.stop_vpn()
        self.on_error("Network connection failed")

    def shared_secret_callback(self):
        self.stop_vpn()
        self.on_error("Shared secrets do not match")
    
    def bind_port_callback(self):
        self.on_error("Failed to bind the specified port")

    def on_error(self, message):
        gtk.gdk.threads_enter()
        md = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
            message)
        md.run()
        md.destroy()
        gtk.gdk.threads_leave()

    def mode_toggled_callback(self, widget, host_label, host_entry, start_button, is_client_mode=True):
        host_label.set_visible(is_client_mode)
        host_entry.set_visible(is_client_mode)

        if is_client_mode:
            start_button.set_label("Connect to Server")
        else:
            start_button.set_label("Start Server")

    def message_received_callback(self, encrypted_message, plaintext_message):
        self.received_cipher_textview.get_buffer().set_text(binascii.b2a_hex(encrypted_message))
        self.received_plain_textview.get_buffer().set_text(plaintext_message)

    def message_sent_callback(self, plaintext_message, encrypted_message, cipher_text_entry):
        cipher_text_entry.set_text(binascii.b2a_hex(encrypted_message))

    def close(self, widget):
        if self.vpn:
            self.vpn.kill()

        gtk.mainquit()

    def __init__(self):
        self.vpn = None

        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_usize(900, 500)
        self.window.set_title("GTK Entry")
        self.window.connect("delete_event", gtk.mainquit)

        hbox = gtk.HBox(gtk.FALSE, 0)
        vbox = gtk.VBox(gtk.FALSE, 0)
        self.window.add(hbox)
        vbox.show()
        hbox.add(vbox)
        hbox.show()

        mode_hbox = gtk.HBox(gtk.FALSE, 0)
        vbox.add(mode_hbox)
        mode_hbox.show()

        host_port_hbox = gtk.HBox(gtk.FALSE, 0)
        vbox.add(host_port_hbox)
        host_port_hbox.show()

        label = gtk.Label("Shared Secret")
        vbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        self.shared_secret_entry = gtk.Entry(50)
        self.shared_secret_entry.connect("activate", self.enter_callback)
        self.shared_secret_entry.set_text("shared_secret")
        self.shared_secret_entry.select_region(0, len(self.shared_secret_entry.get_text()))
        vbox.pack_start(self.shared_secret_entry, gtk.TRUE, gtk.TRUE, 0)
        self.shared_secret_entry.show()

        label = gtk.Label("Plain text")
        vbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        plain_text_entry = gtk.Entry(50)
        plain_text_entry.connect("activate", self.enter_callback, plain_text_entry)
        plain_text_entry.set_text("plain text")
        plain_text_entry.select_region(0, len(plain_text_entry.get_text()))
        vbox.pack_start(plain_text_entry, gtk.TRUE, gtk.TRUE, 0)
        plain_text_entry.show()

        label = gtk.Label("Cipher text")
        vbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        cipher_text_entry = gtk.Entry(50)
        cipher_text_entry.connect("activate", self.enter_callback, cipher_text_entry)
        cipher_text_entry.set_text("cipher text")
        cipher_text_entry.set_editable(False)
        cipher_text_entry.select_region(0, len(cipher_text_entry.get_text()))
        vbox.pack_start(cipher_text_entry, gtk.TRUE, gtk.TRUE, 0)
        cipher_text_entry.show()        

        label = gtk.Label("Mode")
        mode_hbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        host_label = gtk.Label("Server Host")
        host_port_hbox.pack_start(host_label, gtk.TRUE, gtk.TRUE, 0)
        #host_label.show()

        host_entry = gtk.Entry(25)
        host_entry.set_text("localhost")
        host_entry.select_region(0, len(host_entry.get_text()))
        host_port_hbox.pack_start(host_entry, gtk.TRUE, gtk.TRUE, 0)
        #host_entry.show()                   

        label = gtk.Label("Port")
        host_port_hbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        port_entry = gtk.Entry(10)
        port_entry.set_text("6321")
        port_entry.select_region(0, len(port_entry.get_text()))
        host_port_hbox.pack_start(port_entry, gtk.TRUE, gtk.TRUE, 0)
        port_entry.show()     

        send_button = gtk.Button("Send")
        vbox.pack_start(send_button, gtk.TRUE, gtk.TRUE, 0)
        send_button.connect("clicked", self.enter_send_callback, plain_text_entry)
        send_button.show()

        start_button = gtk.Button("Start Server")
        vbox.pack_start(start_button, gtk.TRUE, gtk.TRUE, 0)
        start_button.connect("clicked", self.start_callback, host_entry, port_entry, cipher_text_entry)
        start_button.show()

        server_button = gtk.RadioButton(None, "Server")
        mode_hbox.pack_start(server_button, gtk.TRUE, gtk.TRUE, 0)
        server_button.connect("toggled", self.mode_toggled_callback, host_label, host_entry, start_button, False)
        server_button.set_active(gtk.TRUE)
        server_button.show()

        client_button = gtk.RadioButton(server_button, "Client")
        mode_hbox.pack_start(client_button, gtk.TRUE, gtk.TRUE, 0)
        client_button.connect("toggled", self.mode_toggled_callback, host_label, host_entry, start_button, True)
        client_button.show()

        close_button = gtk.Button("Close")
        close_button.connect_object("clicked", self.close, self.window)
        vbox.pack_start(close_button, gtk.TRUE, gtk.TRUE, 0)
        close_button.set_flags(gtk.CAN_DEFAULT)
        close_button.grab_default()
        close_button.show()
 
        receive_text_vbox = gtk.VBox(gtk.FALSE, 0)
        receive_text_vbox.show()

        label = gtk.Label("Received Cipher Text")
        receive_text_vbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        #scroll bars for received cipher text
        self.scrolled_cipher_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.scrolled_cipher_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        receive_text_vbox.pack_start(self.scrolled_cipher_window, gtk.TRUE, gtk.TRUE, 0)
        self.scrolled_cipher_window.show()

        #recieved cipher textview
        self.received_cipher_textview = gtk.TextView()
        self.scrolled_cipher_window.add_with_viewport(self.received_cipher_textview)
        self.received_cipher_textview.show()

        label = gtk.Label("Received Plain Text")
        receive_text_vbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        #scroll bars for received plain text
        self.scrolled_plain_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.scrolled_plain_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        receive_text_vbox.pack_start(self.scrolled_plain_window, gtk.TRUE, gtk.TRUE, 0)
        self.scrolled_plain_window.show()

        #received plain textview
        self.received_plain_textview = gtk.TextView()
        self.scrolled_plain_window.add_with_viewport(self.received_plain_textview)        
        self.received_plain_textview.show()

        hbox.add(receive_text_vbox)
        self.window.show()

def main():
    gtk.gdk.threads_init()
    gtk.mainloop()
    return 0

if __name__ == "__main__":
    ApplicationGUI()
    main()
