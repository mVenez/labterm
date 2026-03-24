import time
import threading
from typing import Any, Literal

from labterm import Instrument

class Antenna(Instrument):
    """
    This object represents the Pointing Mechanism of an antenna, the system responsible for its movement and general operation.
    You can read the current position of the antenna, set a new target position and move the antenna to reach it.
    Movement happens along two axes, the azimuthal ("az") and the altitude ("alt").
    """
    min_alt = 0
    max_alt = 90 
    
    def __init__(self, channel: int):
        super().__init__(channel)
        self.data: dict[str, Any] = {
            'az': 0.0,
            'alt': self.max_alt,
            'target_az': 0.0,
            'target_alt': self.max_alt,
            'projected_position': (0,self.max_alt)
        }
        self._pointing_thread = None


    def action(self, id: Literal[""], *args):
        "Determines what to do when a DashboardItem is interacted with and dispatches to the relevant method"
        if id == 'measure':
            self._log("Observation started (pretend this is saving interesting astronomical data on your computer)")
        elif id == 'point':
            self.point_thread()
            self._log(f"Pointing command received - Az {self.data['target_az']:.0f}, Alt {self.data['target_alt']:.0f}")
        elif id == 'set_target_az':
            self.data['target_az'] = args[0] % 360
        elif id == 'set_target_alt':
            raw_alt = float(args[0])
            self.data['target_alt'] = max(self.min_alt, min(self.max_alt, raw_alt))


    def update_data(self):
        """
        Updates all the data relative to the antenna, and stores it in the class attributes.

        This is where you would put the code to get feedback on the position of the antenna.
        For now it only updates a utility variable used by the AntennaPosition item.
        """
        self.data['projected_position'] = (self.data['az'], self.data['alt'])


    def _log(self, message):
        """
        Send a message through the set logger function.
        """
        if self.logger:
            self.logger(f"APM: {message}")
    


    def _point_to(self):
        """Simulates the movement of the antenna to point to the target coordinates, following the shortest path"""
        while True:
            diff_az = self.data['target_az'] - self.data['az']
            diff_alt = self.data['target_alt'] - self.data['alt']

            if (abs(diff_az) < 0.5 and abs(diff_alt) < 0.5):
                break

            diff_az = (diff_az + 180) % 360 - 180
            if abs(diff_az) >= 0.5:
                step_az = 0.3 if diff_az > 0 else -0.3
                self.data['az'] = (self.data['az'] + step_az) % 360

            if abs(diff_alt) >= 0.5:
                step_alt = 0.3 if diff_alt > 0 else -0.3
                self.data['alt'] = max(self.min_alt, min(self.max_alt, self.data['alt'] + step_alt))

            self.data['az'] = self.data['az'] % 360
            time.sleep(0.05)

    def point_thread(self) -> None:
        """ 
        Creates a thread to move the antenna without blocking the program.
        """
        def point_sub():
            self._point_to()
        threading.Thread(target=point_sub, daemon=True).start()




