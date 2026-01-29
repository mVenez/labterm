#!/usr/bin/env python3

import curses
import labterm as lt
from power_module import PowerModule


def main(stdscr):
    # Initialise the Dashboard
    dashboard = lt.Dashboard(stdscr)

    # Set Dashboard configuration
    dashboard.set_header("Example: Power Control System")
    dashboard.show_controls(True)   # All the following settings are the same as the default
    dashboard.show_log(True)
    dashboard.set_max_logs(6)
    dashboard.set_update_interval(0.3) # [s]
    dashboard.cycle(True)

    # Define and add the Instruments
    dashboard.add_instruments(PowerModule(0), PowerModule(1))

    # Column and Row alignment, to place the Items
    columns = [0.01, 0.15, 0.25, 0.4, 0.55, 0.65, 0.8]
    rows = [0.13, 0.2, 0.3, 0.4, 0.5]

    # Define and add the Items
    dashboard.add_items(*[
        lt.Label(x=columns[0], y=rows[1], text='Power #1'),
        lt.Label(x=columns[0], y=rows[2], text='Power #2'),
        lt.Label(x=columns[1], y=rows[0], text="State"),
        lt.Label(x=columns[2], y=rows[0], text="HV SET [V]"),
        lt.Label(x=columns[3], y=rows[0], text="HV MON [V]"),
        lt.Label(x=columns[4], y=rows[0], text="I MON [mA]"),

        lt.Switch(x=columns[1], y=rows[1], 
               xgrid=0, ygrid=0, 
               channel=0, data='power', action='power_switch'),
        lt.Switch(x=columns[1], y=rows[2], 
               xgrid=0, ygrid=1, 
               channel=1, data='power', action='power_switch'),

        lt.Editable(x=columns[2], y=rows[1],
                 xgrid = 1, ygrid = 0,
                 channel=0, data='target_voltage', action='set_target', decimals=0),
        lt.Editable(x=columns[2], y=rows[2],
                 xgrid = 1, ygrid = 1,
                 channel=1, data='target_voltage', action='set_target', decimals=0),
        
        lt.Readonly(x=columns[3], y=rows[1], 
                 channel=0, data='actual_voltage', 
                 decimals=0),
        lt.Readonly(x=columns[3], y=rows[2], 
                 channel=1, data='actual_voltage', 
                 decimals=0),

        lt.Readonly(x=columns[4], y=rows[1], 
                 channel=0, data='current', 
                 decimals=0),
        lt.Readonly(x=columns[4], y=rows[2], 
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