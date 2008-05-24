# Copyright (C) 2008 Rodrigo Pinheiro Marques de Araujo
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.



license = """ Copyright (C) 2008 Rodrigo Pinheiro Marques de Araujo

 This program is free software; you can redistribute it and/or modify it under
 the terms of the GNU General Public License as published by the Free Software
 Foundation; either version 2 of the License, or (at your option) any later
 version.

 This program is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 details.

 You should have received a copy of the GNU General Public License along with
 this program; if not, write to the Free Software Foundation, Inc., 51
 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA."""


import gtk
from play import play_events, stop_events, FileFormatError
from record import record_events, stop_record, save_buffer, load_file
import os
import thread
import pynotify


class App(object):


    def __init__(self):
        self.setup_icon()
        self.load_menu()
        self.file_load = None


    def setup_icon(self):
        self.icon = gtk.StatusIcon()
        self.icon.set_from_file("/usr/share/icons/Human/scalable/apps/screensaver.svg")
        self.icon.set_visible(True)
        self.icon.connect('popup_menu', self.popup_menu)


    def load_menu(self):
        self.menu = gtk.Menu()

        start_record = gtk.ImageMenuItem("Start record")
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_MEDIA_RECORD, gtk.ICON_SIZE_MENU)
        start_record.set_image(img)
        start_record.connect('activate', self.menu_item_callback, "SRR")

        stop_record = gtk.ImageMenuItem("Stop record")
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_MEDIA_STOP, gtk.ICON_SIZE_MENU)
        stop_record.set_image(img)
        stop_record.connect('activate', self.menu_item_callback, "STR")

        start_events = gtk.ImageMenuItem("Start events")
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
        start_events.set_image(img)
        start_events.connect('activate', self.menu_item_callback, "SRE")

        stop_events = gtk.ImageMenuItem("Stop events")
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_MEDIA_STOP, gtk.ICON_SIZE_MENU)
        stop_events.set_image(img)
        stop_events.connect('activate', self.menu_item_callback, "STE")

        save_events = gtk.ImageMenuItem("Save events")
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_SAVE, gtk.ICON_SIZE_MENU)
        save_events.set_image(img)
        save_events.connect('activate', self.menu_item_callback, "SEV")

        load_events = gtk.ImageMenuItem("Load events")
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU)
        load_events.set_image(img)
        load_events.connect('activate', self.menu_item_callback, "LEV")
        
        about = gtk.ImageMenuItem("About")
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU)
        about.set_image(img)
        about.connect('activate', self.menu_item_callback, "About")

        exit = gtk.ImageMenuItem("Exit")
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU)
        exit.set_image(img)
        exit.connect('activate', self.menu_item_callback, "Exit")

        self.menu.append(start_record)
        self.menu.append(stop_record)
        self.menu.append(gtk.SeparatorMenuItem())

        self.menu.append(save_events)
        self.menu.append(load_events)
        self.menu.append(gtk.SeparatorMenuItem())

        self.menu.append(start_events)
        self.menu.append(stop_events)
        self.menu.append(gtk.SeparatorMenuItem())

        self.menu.append(about)
        self.menu.append(exit)

        self.menu.show_all()


    def menu_item_callback(self, widget, item):
        if item ==  "SRR":
            gtk.gdk.threads_init()
            thread.start_new_thread(record_events, ())
            gtk.gdk.threads_leave()
        elif item == "STR":
            stop_record()
        elif item == "SRE":
            gtk.gdk.threads_init()
            thread.start_new_thread(play_events, (self.show_notify_error,))
            gtk.gdk.threads_leave()
        elif item == "STE":
            stop_events()
        elif item == "SEV":
            self.save_events()
        elif item == "LEV":
            self.load_events()
        elif item == "About":
            self.show_about()
        else:
            stop_record()
            stop_events()
            gtk.main_quit()


    def show_notify_error(self):
        notification = pynotify.Notification("Bad file formart", 
                                             ("File %s contains no valid format.\n" + 
                                             "Please, load another file.") % self.file_load, "stock_stop" )
        notification.set_timeout(5000)
        notification.set_urgency(pynotify.URGENCY_CRITICAL)
        notification.attach_to_status_icon(self.icon)
        notification.show()


    def show_about(self):
        self.about = gtk.AboutDialog()
        self.about.set_name("Xrecord")
        self.about.set_version("0.1")
        self.about.set_comments("Grava e reproduz eventos do X")
        self.about.set_copyright("Copyright (C) 2008 Rodrigo Pinheiro Marques de Araujo")
        self.about.set_authors(["Rodrigo Pinheiro Marques de Araujo"])
        self.about.set_license(license)
        self.about.set_program_name("Xrecord")
        self.about.set_website("http://linil.wordpress.com")
        self.about.run()
        self.about.destroy()


    def overwrite_file(self, path):
        msg = "Overwrite %s?" % path
        dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_YES_NO, msg)
        response = dialog.run()
        dialog.destroy()
        return response == gtk.RESPONSE_YES


    def load_events(self):
        filechooser = gtk.FileChooserDialog("Load...", 
                                            None, 
                                            gtk.FILE_CHOOSER_ACTION_OPEN, 
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                            gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        filechooser.set_default_response(gtk.RESPONSE_OK)
        filechooser.set_current_folder(os.environ["HOME"])

        while True:

            response = filechooser.run()

            if response == gtk.RESPONSE_OK:
                path = filechooser.get_filename()
                try:
                    load_file(path)
                    self.file_load = path
                    break
                except IOError:
                    dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Permission denied!")
                    dialog.run()
                    dialog.destroy()
            else:
                break
        filechooser.destroy()

    def save_events(self):
        filechooser = gtk.FileChooserDialog("Save...", 
                                            None, 
                                            gtk.FILE_CHOOSER_ACTION_SAVE, 
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                            gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        filechooser.set_default_response(gtk.RESPONSE_OK)
        filechooser.set_current_folder(os.environ["HOME"])

        path = None

        while True:
            response = filechooser.run()

            if response != gtk.RESPONSE_OK:
                path = None
                break

            path = filechooser.get_filename()

            if os.path.exists(path):
                if not self.overwrite_file(path):
                    continue

            if path != None:
                try:
                    save_buffer(path)
                    break
                except IOError:
                    dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Permission denied!")
                    dialog.run()
                    dialog.destroy()

        
        filechooser.destroy()

 

    def popup_menu(self, widget, button, ctime):
        self.menu.popup(None, None, gtk.status_icon_position_menu, button, ctime, widget)

    def run(self):
        pynotify.init("Xrecord")
        gtk.main()



if __name__ == "__main__":
    App().run()
