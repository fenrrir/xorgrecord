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



import os
import sys

import Xlib.display
import Xlib.X
from Xlib import XK
import Xlib.error
import Xlib.ext.xtest
from Xlib import X, XK, display

from Xlib.protocol import rq

from time import sleep, time


try:
    from Xlib.ext import record
except ImportError:
    print "RECORD extension not found"
    sys.exit(1)





class FileFormatError(Exception):
    pass


class EventRepeater(object):

    def __init__(self):
        self.display = Xlib.display.Display()
        self.stop = False
        self.buffer = None

    def _key_to_code(self, key):
        new_key = getattr(XK, "XK_" + key)
        code = self.display.keysym_to_keycode(new_key)
        return code


    def _mouse(self, button, action=Xlib.X.ButtonPress): #button= 1 left, 2 middle, 3 right
        Xlib.ext.xtest.fake_input(self.display, action, int(button) )
        self.display.sync()


    def mouse_press(self, button):
        self._mouse(button)

    def mouse_release(self, button):
        self._mouse(button, action=Xlib.X.ButtonRelease)


    def mouse_motion(self, x,y):
        Xlib.ext.xtest.fake_input(self.display, Xlib.X.MotionNotify, x=int(x), y=int(y))
        self.display.sync()


    def _key(self, key, action=Xlib.X.KeyPress):
        Xlib.ext.xtest.fake_input(self.display, action, self._key_to_code(key))
        self.display.sync()

    def key_press(self, key):
        self._key(key)


    def key_release(self, key):
        self._key(key, action= Xlib.X.KeyRelease )

    def my_sleep(self, ticks):
        sleep(float(ticks))


    def play_events(self, error_callback=None):
        self.stop = False
        functions = {}
        functions["ButtonPress"] = self.mouse_press
        functions["ButtonRelease"] = self.mouse_release
        functions["MotionNotify"] = self.mouse_motion
        functions["KeyStrRelease"] = self.key_release
        functions["KeyStrPress"] = self.key_press
        functions["Sleep"] = self.my_sleep
        for items in self.buffer:
            if self.stop:
                self.stop = False
                break

            command_args = items.split()
            command = command_args[0]
            args = command_args[1:]
            try:
                functions[command](*args)
            except KeyError, e:
                if not error_callback:
                    raise FileFormatError()
                else:
                    error_callback()




class EventRecorder(object):

    def __init__(self):
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        self.buffer = []
        self.time = None
        self.stop = False
        self.ctx = None
        if not self.record_dpy.has_extension("RECORD"):
            print "RECORD extension not found"
            sys.exit(1)

    
    def insert_sleep(self):
        if not self.time:
            self.time = time()
        current = time()
        self.buffer.append("Sleep %s" % (current - self.time) )
        self.time = current



    def lookup_keysym(self, keysym):
        for name in dir(XK):
            if name[:3] == "XK_" and getattr(XK, name) == keysym:
                return name[3:]
        return "[%d]" % keysym


    def save_buffer(self, filename):
        f_output = file(filename, "w")
        f_output.write( "\n".join(self.buffer) )
        f_output.close()


    def load_file(self, filename):
        f_input = file(filename)
        for line in f_input:
            self.buffer.append(line)
        f_input.close()



    def record_callback(self, reply):

        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            print "* received swapped protocol data, cowardly ignored"
            return
        if not len(reply.data) or ord(reply.data[0]) < 2:
            # not an event
            return

        if self.stop:
            self.stop = False
            self.local_dpy.record_disable_context(self.ctx)
            self.local_dpy.flush()
            return

        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, 
                                                    self.record_dpy.display, 
                                                    None, 
                                                    None)

            if event.type in [X.KeyPress, X.KeyRelease]:
                pr = event.type == X.KeyPress and "Press" or "Release"

                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                if not keysym:
                    print "KeyCode%s" % pr, event.detail
                else:
                    self.buffer.append( "KeyStr%s %s" % (pr, self.lookup_keysym(keysym)) )
                    if pr == "Release":
                        self.insert_sleep()

                if event.type == X.KeyPress and keysym == XK.XK_Escape:
                    local_dpy.record_disable_context(self.ctx)
                    local_dpy.flush()
                    return
            elif event.type == X.ButtonPress:
                self.buffer.append( "ButtonPress %s" % event.detail )
                self.insert_sleep()
            elif event.type == X.ButtonRelease:
                self.buffer.append( "ButtonRelease %s" % event.detail)
                self.insert_sleep()
            elif event.type == X.MotionNotify:
                self.buffer.append( "MotionNotify %s %s" % ( event.root_x, event.root_y ) )
                self.insert_sleep()



    def record_events(self):
        self.time = None
        self.buffer = []
        self.stop = False
        # Create a recording context; we only want key and mouse events
        self.ctx = self.record_dpy.record_create_context(
                0,
                [record.AllClients],
                [{
                        'core_requests': (0, 0),
                        'core_replies': (0, 0),
                        'ext_requests': (0, 0, 0, 0),
                        'ext_replies': (0, 0, 0, 0),
                        'delivered_events': (0, 0),
                        'device_events': (X.KeyPress, X.MotionNotify),
                        'errors': (0, 0),
                        'client_started': False,
                        'client_died': False,
                }])
        # Enable the context; this only returns after a call to record_disable_context,
        # while calling the callback function in the meantime
        self.record_dpy.record_enable_context(self.ctx, self.record_callback)
        # Finally free the context
        self.record_dpy.record_free_context(self.ctx)

