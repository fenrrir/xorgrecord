#!/usr/bin/env python
import Xlib.display
import Xlib.X
from Xlib import XK
import Xlib.error
import Xlib.ext.xtest
import sys
from time import sleep
import record
import gtk

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

def play_events():
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
            dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Xrecord: File Format Error")
            dialog.run()
            dialog.destroy()


