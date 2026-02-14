#!/usr/bin/env python3
"""
01 - Getting Started Example
=======================

The simplest possible *functional* dashboard: a single instrument with a switch
and a read-only value. A good starting point for new users.

Run with:
    python3 examples/01_getting_started/main.py
"""

import curses
import random
import labterm as lt


# ============================== Mock Instrument ============================= #

class SimpleInstrument(lt.Instrument):
    """
    A minimal mock instrument.

    Simulates a device that can be turned on or off and produces
    a single noisy measurement when active.
    """

    def __init__(self, channel: int):
        super().__init__(channel)
        self.data = {
            'power': False,
            'value': 0.0,
        }

    def update_data(self) -> None:
        if self.data['power']:
            # Simulate a noisy measurement
            self.data['value'] = 50.0 + random.uniform(-5.0, 5.0)
        else:
            self.data['value'] = 0.0

    def action(self, action_id: str, *args) -> None:
        if action_id == 'toggle_power':
            self.data['power'] = not self.data['power']
            state = 'ON' if self.data['power'] else 'OFF'
            self._log(f"Power turned {state}")

    def _log(self, message: str) -> None:
        if self.logger:
            self.logger(message)


# ================================= Dashboard ================================ #

def main(stdscr):
    # Initialise the Dashboard
    dashboard = lt.Dashboard(stdscr, cycle=True)

    # Set Dashboard configuration
    dashboard.set_header("Example: Getting Started")

    # Define and add the Instruments
    dashboard.add_instruments(SimpleInstrument(channel=0))

    # Define and add the DashboardItems
    dashboard.add_items(*[
        # Column headers
        lt.Label(x=0.15, y=0.20, text="Power"),
        lt.Label(x=0.35, y=0.20, text="Value"),

        # Row label
        lt.Label(x=0.05, y=0.30, text="Device"),

        # Controls
        lt.Switch(
            x=0.15, y=0.30,
            xgrid=0, ygrid=0,
            channel=0, data='power', action='toggle_power'
        ),
        lt.Readonly(
            x=0.35, y=0.30,
            channel=0, data='value',
            decimals=1, text_after=" units"
        ),
    ])


    try:
        dashboard.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    curses.wrapper(main)