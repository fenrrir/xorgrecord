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

import Xlib.display
import Xlib.X
from Xlib import XK
import Xlib.error
import Xlib.ext.xtest
import sys
from time import sleep
import record

class FileFormatError(Exception):
    pass


display = Xlib.display.Display()

_global_stop = False

def key_to_code(key):
    new_key = getattr(XK, "XK_" + key)
    code = display.keysym_to_keycode(new_key)
    return code

def mouse_press(button): #button= 1 left, 2 middle, 3 right
    Xlib.ext.xtest.fake_input(display,Xlib.X.ButtonPress, int(button) )
    display.sync()


def mouse_release(button):
    Xlib.ext.xtest.fake_input(display,Xlib.X.ButtonRelease, int(button) )
    display.sync()


def mouse_motion(x,y):
    Xlib.ext.xtest.fake_input(display,Xlib.X.MotionNotify, x=int(x), y=int(y))
    display.sync()


def key_press(key):
    Xlib.ext.xtest.fake_input(display,Xlib.X.KeyPress, key_to_code(key))
    display.sync()


def key_release(key):
    Xlib.ext.xtest.fake_input(display,Xlib.X.KeyRelease, key_to_code(key))
    display.sync()

def my_sleep(ticks):
    sleep(float(ticks))

def stop_events():
    global _global_stop 
    _global_stop = True

def play_events(error_callback=None):
    global _global_stop

    functions = {}
    functions["ButtonPress"] = mouse_press
    functions["ButtonRelease"] = mouse_release
    functions["MotionNotify"] = mouse_motion
    functions["KeyStrRelease"] = key_release
    functions["KeyStrPress"] = key_press
    functions["Sleep"] = my_sleep
    for items in record.buffer:
        if _global_stop:
            _global_stop = False
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
