#!/usr/bin/env python

import dbus
import gobject

class NetworkManagerStateChangeHandler(object):
    from dbus.mainloop.glib import DBusGMainLoop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    proxy = bus.get_object('org.freedesktop.NetworkManager',
                           '/org/freedesktop/NetworkManager',)
    iface = dbus.Interface(proxy, 'org.freedesktop.NetworkManager')

    def __init__(self, connect_handler=None, disconnect_handler=None):
        self.connect_handler = connect_handler
        self.disconnect_handler = disconnect_handler
        self.enable()

    def enable(self):
        # This will guarantee that an action is run immediately.
        self.last_connection_status = not self.connected()
        self.handle_state_change()
        NetworkManagerStateChangeHandler.iface.connect_to_signal('StateChanged', self.handle_state_change)

    def connected(self):
        """Returns True if current state is connected, else False."""
        return NetworkManagerStateChangeHandler.iface.state() == 3

    def handle_state_change(self, *args):
        """If Network Manager has just connected or disconnected, call
        the appropriate handler."""
        new_connection_status = self.connected()
        if new_connection_status != self.last_connection_status:
            if new_connection_status:
                self.connect_handler()
            else:
                self.disconnect_handler()
        self.last_connection_status = new_connection_status

if __name__ == '__main__':
    import plac
    import os
    @plac.annotations(
        # opt=(helptext, kind, abbrev, type, choices, metavar)
        connect_command=('Command to be run when NetworkManager connects to the internet.', 'positional'),
        disconnect_command=('Command to be run when NetworkManager disconnects from the internet.', 'positional')
        )
    def main(connect_command, disconnect_command):
        """Set up commands to be run when Network Manager connects or disconnects."""
        def connect_handler():
            print "Connected."
            os.system(connect_command)
        def disconnect_handler():
            print "Disconnected."
            os.system(disconnect_command)
        handler = NetworkManagerStateChangeHandler(connect_handler, disconnect_handler)
        loop = gobject.MainLoop()
        loop.run()
    plac.call(main)
