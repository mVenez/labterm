#!/usr/bin/env python3
"""
04 - Antenna Pointing Mechanism Example
=======================

This example includes a custom DashboardItem (defined in `antenna_position.py`), capable of showing the current orientation of the controlled antenna.

Run with:
    python3 examples/04_antenna/main.py
"""
import curses
import labterm as lt
from antenna import Antenna
from antenna_position import AntennaPosition


def main(stdscr):
    # Initialise the Dashboard
    dashboard = lt.Dashboard(stdscr)

    # Set Dashboard configuration
    dashboard.set_header("Example: Antenna Pointing Mechanism")

    # Define and add the Instruments
    dashboard.add_instruments(Antenna(0))

    # Column and Row alignment, to place the Items
    columns = [0.01, 0.15, 0.25, 0.4, 0.55, 0.65, 0.8]
    rows = [0.13, 0.2, 0.3, 0.4, 0.5]

    # Define and add the Items
    dashboard.add_items(*[
        lt.Header(x=4, y=rows[0], yoffset=-1, text="APM", xycoords='yprop'),

        lt.Label(x=columns[1], y=rows[0], text="Target"),
        lt.Label(x=columns[2], y=rows[0], text="Current position"),
        lt.Label(x=columns[0], y=rows[1], text = "Az"),
        lt.Label(x=columns[0], y=rows[2], text = "Alt"),

        lt.Editable(x=columns[1], y=rows[1],
                 xgrid = 0, ygrid = 0,
                 channel=0, data='target_az', action='set_target_az', decimals=0),
        lt.Editable(x=columns[1], y=rows[2],
                 xgrid = 0, ygrid = 1,
                 channel=0, data='target_alt', action='set_target_alt', decimals=0, initial_value=90, valign='bottom'),
        lt.Readonly(x=columns[2], y=rows[1], 
                 channel=0, data='az', 
                 decimals=0),
        lt.Readonly(x=columns[2], y=rows[2], 
                 channel=0, data='alt', initial_value=90,
                 decimals=0),
                 
        lt.Button(x=columns[1], y=rows[3], 
                  xgrid=0, ygrid=2, channel=0, 
                  text="Point Antenna", action="point"),
        
        AntennaPosition(x=0.75, y=0.3, 
                        channel=0, data='projected_position', 
                        valign='center', halign='center')
    ])

    try:
        dashboard.run()
    except KeyboardInterrupt:
        pass
    finally:
        pass

if __name__ == "__main__":
    curses.wrapper(main)