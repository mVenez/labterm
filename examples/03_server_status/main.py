#!/usr/bin/env python3
"""
03 - Server Status Example
=======================

A slightly different application: this dashboard continuously pings three ip addresses and shows a green light if it receives an answer, and red otherwise. LabTerm can be used for remote control, too!

Run with:
    python3 examples/03_server_status/main.py
"""
import curses
import labterm as lt
from tester import ServerTester


def main(stdscr):
    # Initialise the Dashboard
    dashboard = lt.Dashboard(stdscr, data_update_interval=2)

    # Set Dashboard configuration
    dashboard.set_header("Example: server status check")
    # ... here you can customize the dashboard behaviour to your liking

    # Define and add the Instruments
    dashboard.add_instruments(ServerTester(0, 'github.com'),
                              ServerTester(1, 'localhost'),
                              ServerTester(2, 'mysite'))

    # Define and add the Items
    dashboard.add_items(*[
        lt.Light(x=0.1, y=0.2, channel=0, data='online'),
        lt.Light(x=0.1, y=0.3, channel=1, data='online'),
        lt.Light(x=0.1, y=0.4, channel=2, data='online'),

        lt.Label(x=0.1, xoffset=2, y=0.2, text='github.com'),
        lt.Label(x=0.1, xoffset=2, y=0.3, text='localhost'),
        lt.Label(x=0.1, xoffset=2, y=0.4, text='mysite')
    ])

    try:
        dashboard.run()
    except KeyboardInterrupt:
        pass
    finally:
        pass

if __name__ == "__main__":
    curses.wrapper(main)