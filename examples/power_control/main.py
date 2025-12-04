#!/usr/bin/env python

import curses
from labterm import Dashboard, Label, Switch, Editable, Readonly
from power_module import PowerModule


def main(stdscr):

    dashboard = Dashboard(stdscr)

    dashboard.set_header("Testing the library")

    dashboard.add_instruments(PowerModule(0), PowerModule(1))

    columns = [0.01, 0.15, 0.25, 0.4, 0.55, 0.65, 0.8]
    rows = [0.13, 0.2, 0.3, 0.4, 0.5]

    dashboard.add_items(*[
        Label(x=columns[0], y=rows[1], text='Power #1'),
        Label(x=columns[0], y=rows[2], text='Power #2'),
        Label(x=columns[1], y=rows[0], text="State"),
        Label(x=columns[2], y=rows[0], text="HV SET [V]"),
        Label(x=columns[3], y=rows[0], text="HV MON [V]"),
        Label(x=columns[4], y=rows[0], text="I MON [mA]"),

        Switch(x=columns[1], y=rows[1], 
               xgrid=0, ygrid=0, 
               channel=0, data='power', action='power_switch'),
        Switch(x=columns[1], y=rows[2], 
               xgrid=0, ygrid=1, 
               channel=1, data='power', action='power_switch'),

        Editable(x=columns[2], y=rows[1],
                 xgrid = 1, ygrid = 0,
                 channel=0, data='target_voltage', action='set_target', decimals=0),
        Editable(x=columns[2], y=rows[2],
                 xgrid = 1, ygrid = 1,
                 channel=1, data='target_voltage', action='set_target', decimals=0),
        
        Readonly(x=columns[3], y=rows[1], 
                 channel=0, data='actual_voltage', 
                 decimals=0),
        Readonly(x=columns[3], y=rows[2], 
                 channel=1, data='actual_voltage', 
                 decimals=0),

        Readonly(x=columns[4], y=rows[1], 
                 channel=0, data='current', 
                 decimals=0),
        Readonly(x=columns[4], y=rows[2], 
                 channel=1, data='current', 
                 decimals=0),
    ])

    try:
        dashboard.run()
    except KeyboardInterrupt:
        pass
    finally:
        pass

if __name__ == "__main__":
    curses.wrapper(main)