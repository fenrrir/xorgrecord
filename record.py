#!/usr/bin/python
#
# $Id: record_demo.py,v 1.2 2007/06/10 14:11:59 mggrant Exp $
#
# examples/record_demo.py -- demonstrate record extension
#
#    Copyright (C) 2006 Alex Badea <vamposdecampos@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Simple demo for the RECORD extension
# Not very much unlike the xmacrorec2 program in the xmacro package.

__all__ = ('record_events', 'buffer', 'save_buffer', 'load_file', 'stop_record')

import sys
import os

# Change path so we find Xlib
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq
from time import time


local_dpy = display.Display()
record_dpy = display.Display()

buffer = []

global_time = None
_global_stop = False
_global_ctx = None

def insert_sleep():
    global global_time
    if not global_time:
        global_time = time()
    current = time()
    buffer.append("Sleep %s" % (current - global_time) )
    global_time = current



def lookup_keysym(keysym):
    for name in dir(XK):
        if name[:3] == "XK_" and getattr(XK, name) == keysym:
            return name[3:]
    return "[%d]" % keysym


def save_buffer(filename):
    f_output = file(filename, "w")
    f_output.write("\n".join(buffer))
    f_output.close()


def load_file(filename):
    f_input = file(filename)
    for line in f_input:
        buffer.append(line)
    f_input.close()


def stop_record():
    global _global_stop 
    _global_stop = True


def record_callback(reply):
    global _global_stop
    print "event"

    if reply.category != record.FromServer:
        return
    if reply.client_swapped:
        print "* received swapped protocol data, cowardly ignored"
        return
    if not len(reply.data) or ord(reply.data[0]) < 2:
        # not an event
        return

    if _global_stop:
        _global_stop = False
        local_dpy.record_disable_context(_global_ctx)
        local_dpy.flush()
        return

    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, record_dpy.display, None, None)

        if event.type in [X.KeyPress, X.KeyRelease]:
            pr = event.type == X.KeyPress and "Press" or "Release"

            keysym = local_dpy.keycode_to_keysym(event.detail, 0)
            if not keysym:
                print "KeyCode%s" % pr, event.detail
            else:
                buffer.append( "KeyStr%s %s" % (pr, lookup_keysym(keysym)) )
                if pr == "Release":
                    insert_sleep()

            if event.type == X.KeyPress and keysym == XK.XK_Escape:
                local_dpy.record_disable_context(_global_ctx)
                local_dpy.flush()
                return
        elif event.type == X.ButtonPress:
            buffer.append( "ButtonPress %s" % event.detail )
            insert_sleep()
        elif event.type == X.ButtonRelease:
            buffer.append( "ButtonRelease %s" % event.detail)
            insert_sleep()
        elif event.type == X.MotionNotify:
            buffer.append( "MotionNotify %s %s" % ( event.root_x, event.root_y ) )
            insert_sleep()



def record_events():
    global _global_ctx
    # Create a recording context; we only want key and mouse events
    _global_ctx = record_dpy.record_create_context(
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
    record_dpy.record_enable_context(_global_ctx, record_callback)
    # Finally free the context
    record_dpy.record_free_context(_global_ctx)



# Check if the extension is present
if not record_dpy.has_extension("RECORD"):
    print "RECORD extension not found"
    sys.exit(1)


