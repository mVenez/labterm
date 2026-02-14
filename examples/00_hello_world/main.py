#!/usr/bin/env python3
"""
01 - Hello, World! Example
=======================

The simplest possible dashboard: a single static text placed wherever you want.

Run with:
    python3 examples/00_hello_world/main.py
"""

import curses
import labterm as lt

def main(stdscr) -> None:
    # Initialise the Dashboard
    dashboard = lt.Dashboard(stdscr)

    dashboard.show_log(False)
    # dashboard.show_controls(False) # you could also hide the controls

    # Add some text to the dashboard
    dashboard.add_items(
        lt.Label(x=0.5, y=0.5, text="Hello, World!")
        )
    

    # === EXTRA ===
    # You could try and position the text differently. Try uncommenting these following lines:
    # dashboard.add_items(
    #     lt.Label(x=1, y=6, xycoords='int',
    #              text="Hello, World! (the return)", )
    #     # Here we've chosen an exact row and column to print the text to
    #     )
    # dashboard.add_items(
    #     lt.Label(x=18, y=8, xycoords='int', halign='center',
    #              text="Hello, World! (hello again)")
    #     # Here we've chosen to center the text horizontally
    #     )
    # =============


    try:
        dashboard.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    curses.wrapper(main)