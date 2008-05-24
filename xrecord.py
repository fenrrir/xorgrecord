import gtk
from play import play_events, stop_events
from record import record_events, stop_record, save_buffer, load_file
import thread


class App(object):


    def __init__(self):
        self.load_menu()


    def load_menu(self):
        self.menu = gtk.Menu()

        start_record = gtk.MenuItem("Start record")
        start_record.connect('activate', self.menu_item_callback, "SRR")

        stop_record = gtk.MenuItem("Stop record")
        stop_record.connect('activate', self.menu_item_callback, "STR")

        start_events = gtk.MenuItem("Start events")
        start_events.connect('activate', self.menu_item_callback, "SRE")

        stop_events = gtk.MenuItem("Stop events")
        stop_events.connect('activate', self.menu_item_callback, "STE")

        save_events = gtk.MenuItem("Save events")
        save_events.connect('activate', self.menu_item_callback, "SEV")

        load_events = gtk.MenuItem("Load events")
        load_events.connect('activate', self.menu_item_callback, "LEV")

        self.menu.append(start_record)
        self.menu.append(stop_record)
        self.menu.append(gtk.SeparatorMenuItem())

        self.menu.append(save_events)
        self.menu.append(load_events)
        self.menu.append(gtk.SeparatorMenuItem())

        self.menu.append(start_events)
        self.menu.append(stop_events)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.show_all()


    def menu_item_callback(self, widget, item):
        if item ==  "SRR":
            record_events()
        elif item == "STR":
            stop_record()
        elif item == "SRE":
            play_events()
        else:
            stop_events()


    def popup_menu(self, widget, button, ctime):
        self.menu.popup(None, None, gtk.status_icon_position_menu, button, ctime, widget)

    def run(self):
        icon = gtk.StatusIcon()
        icon.set_from_file("/usr/share/icons/Tangerine/scalable/places/network-server.svg")
        icon.set_visible(True)
        icon.connect('popup_menu', self.popup_menu)
        gtk.main()



if __name__ == "__main__":
    App().run()
