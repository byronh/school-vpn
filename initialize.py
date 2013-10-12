#!/usr/bin/env python
import gtk

from vpnserver import VPNServer
from vpnclient import VPNClient

class ApplicationGUI:
    def __init__(self):
        self.server = None
        self.client = None

    def enter_callback(self, widget, entry):
        entry_text = entry.get_text()
        print "Entry contents: %s\n" % entry_text

    def enter_send_callback(self, widget, entry):
        entry_text = entry.get_text()
        print "Send this text: %s\n" % entry_text    

    def start_server_callback(self, widget, port_entry, shared_secret_entry):
        # TODO: catch exceptions such as not being able to bind on port
        self.server = VPNServer(int(port_entry.get_text()), shared_secret_entry.get_text())
        self.server.add_message_received_callback(self.message_received_callback)
        self.server.start()

    def connect_callback(self, widget, host_entry, port_entry, shared_secret_entry):
        # TODO: handle authentication errors and connection errors
        self.client = VPNClient(
                host_entry.get_text(), int(port_entry.get_text()), shared_secret_entry.get_text())
        self.client.add_message_received_callback(self.message_received_callback)
        self.client.start()

    def entry_toggle_editable(self, checkbutton, entry):
        entry.set_editable(checkbutton.get_active())

    def entry_toggle_visibility(self, checkbutton, entry):
        entry.set_visibility(checkbutton.get_active())

    def message_received_callback(self, encrypted_message, plaintext_message):
        # TODO: display the message
        pass

    def __init__(self):
        # create a new window
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_usize(600, 500)
        window.set_title("GTK Entry")
        window.connect("delete_event", gtk.mainquit)

        vbox = gtk.VBox(gtk.FALSE, 0)
        window.add(vbox)
        vbox.show()

        mode_hbox = gtk.HBox(gtk.FALSE, 0)
        vbox.add(mode_hbox)
        mode_hbox.show()

        host_port_hbox = gtk.HBox(gtk.FALSE, 0)
        vbox.add(host_port_hbox)
        host_port_hbox.show()

        label = gtk.Label("Shared Secret")
        vbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        shared_secret_entry = gtk.Entry(50)
        shared_secret_entry.connect("activate", self.enter_callback, shared_secret_entry)
        shared_secret_entry.set_text("Shared secret")
        shared_secret_entry.select_region(0, len(shared_secret_entry.get_text()))
        vbox.pack_start(shared_secret_entry, gtk.TRUE, gtk.TRUE, 0)
        shared_secret_entry.show()

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
        cipher_text_entry.set_text("cipher")
        cipher_text_entry.append_text(" text")
        cipher_text_entry.select_region(0, len(cipher_text_entry.get_text()))
        vbox.pack_start(cipher_text_entry, gtk.TRUE, gtk.TRUE, 0)
        cipher_text_entry.show()        

        label = gtk.Label("Mode")
        mode_hbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        server_button = gtk.RadioButton(None, "Server")
        mode_hbox.pack_start(server_button, gtk.TRUE, gtk.TRUE, 0)
        server_button.connect("toggled", self.entry_toggle_editable, plain_text_entry)
        server_button.set_active(gtk.TRUE)
        server_button.show()

        client_button = gtk.RadioButton(server_button, "Client")
        mode_hbox.pack_start(client_button, gtk.TRUE, gtk.TRUE, 0)
        client_button.connect("toggled", self.entry_toggle_editable, plain_text_entry)
        client_button.show()

        label = gtk.Label("Server Host")
        host_port_hbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        host_entry = gtk.Entry(10)
        host_entry.set_text("host")
        host_entry.select_region(0, len(host_entry.get_text()))
        host_port_hbox.pack_start(host_entry, gtk.TRUE, gtk.TRUE, 0)
        host_entry.show()                   

        label = gtk.Label("Port")
        host_port_hbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        port_entry = gtk.Entry(10)
        port_entry.set_text("port")
        port_entry.select_region(0, len(port_entry.get_text()))
        host_port_hbox.pack_start(port_entry, gtk.TRUE, gtk.TRUE, 0)
        port_entry.show()     

        send_button = gtk.Button("Send")
        vbox.pack_start(send_button, gtk.TRUE, gtk.TRUE, 0)
        send_button.connect("clicked", self.enter_send_callback, plain_text_entry)
        send_button.show()

        start_server_button = gtk.Button("Start Server")
        vbox.pack_start(start_server_button, gtk.TRUE, gtk.TRUE, 0)
        start_server_button.connect("clicked", self.start_server_callback, port_entry, shared_secret_entry)
        start_server_button.show()

        close_button = gtk.Button("Close")
        close_button.connect_object("clicked", gtk.mainquit, window)
        vbox.pack_start(close_button, gtk.TRUE, gtk.TRUE, 0)
        close_button.set_flags(gtk.CAN_DEFAULT)
        close_button.grab_default()
        close_button.show()
 
        label = gtk.Label("Received Text")
        vbox.pack_start(label, gtk.TRUE, gtk.TRUE, 0)
        label.show()

        textview = gtk.TextView()
        vbox.pack_start(textview, gtk.TRUE, gtk.TRUE, 0)
        textview.show()

        window.show()

def main():
    gtk.mainloop()
    return 0

if __name__ == "__main__":
    ApplicationGUI()
    main()
