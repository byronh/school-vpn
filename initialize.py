import gtk

class EntryExample:
    def enter_callback(self, widget, entry):
        entry_text = entry.get_text()
        print "Entry contents: %s\n" % entry_text

    def entry_toggle_editable(self, checkbutton, entry):
        entry.set_editable(checkbutton.active)

    def entry_toggle_visibility(self, checkbutton, entry):
        entry.set_visibility(checkbutton.active)

    def __init__(self):
        # create a new window
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_usize(300, 100)
        window.set_title("GTK Entry")
        window.connect("delete_event", gtk.mainquit)

        vbox = gtk.VBox(gtk.FALSE, 0)
        window.add(vbox)
        vbox.show()

        entry = gtk.Entry(50)
        entry.connect("activate", self.enter_callback, entry)
        entry.set_text("hello")
        entry.append_text(" world")
        entry.select_region(0, len(entry.get_text()))
        vbox.pack_start(entry, gtk.TRUE, gtk.TRUE, 0)
        entry.show()

        hbox = gtk.HBox(gtk.FALSE, 0)
        vbox.add(hbox)
        hbox.show()
                                  
        check = gtk.CheckButton("Editable")
        hbox.pack_start(check, gtk.TRUE, gtk.TRUE, 0)
        check.connect("toggled", self.entry_toggle_editable, entry)
        check.set_active(gtk.TRUE)
        check.show()
    
        check = gtk.CheckButton("Visible")
        hbox.pack_start(check, gtk.TRUE, gtk.TRUE, 0)
        check.connect("toggled", self.entry_toggle_visibility, entry)
        check.set_active(gtk.TRUE)
        check.show()
                                   
        button = gtk.Button("Close")
        button.connect_object("clicked", gtk.mainquit, window)
        vbox.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
        button.set_flags(gtk.CAN_DEFAULT)
        button.grab_default()
        button.show()
        window.show()

def main():
    gtk.mainloop()
    return 0

if __name__ == "__main__":
    EntryExample()
    main()