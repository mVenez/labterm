import time
import threading
import random
from typing import Any, Literal

from labterm import Instrument

class PowerModule(Instrument):
    """
    Power module
    """
    min_voltage = 800 # [V]
    max_voltage = 2200 # [V]
    
    def __init__(self, channel: int, savestate_directory: str = '.', pulse_delay: float = 1):
        super().__init__(channel)
        self.data: dict[str, Any] = {
            'target_voltage': self.min_voltage, # [V]
            'actual_voltage': self.min_voltage, # [V]
            'power': False, # True or False, corresponds to on/off
            'current': 0.0, # [mA]
        }
        self._ramping : bool = False # security block to stop other functions while ramping


    def action(self, id: Literal["power_switch", "set_target", "pulser_switch"], *args):
        "Determines what to do when a DashboardItem is interacted with and dispatches to the relevant method"
        if id == "power_switch":
            if self.data['power']:
                self._turn_off()
            else:
                self._turn_on()
        elif id == "set_target":
            self._set_target(args[0])


    def update_data(self):
        """
        Updates all the data relative to the power module, and stores it in the class attributes.
        """
        self.data['current'] = self._get_current()
        self.data['actual_voltage']  = self._get_actual_voltage()


    def _log(self, message):
        """
        Send a message through the set logger function.
        """
        if self.logger:
            self.logger(f"Power {self.channel}: {message}")
    
    
    def _get_actual_voltage(self) -> float:
        """
        Measured voltage in V
        """
        return self.data['actual_voltage'] + random.normalvariate(0,0.5)
    
    def _get_current(self) -> float:
        """Measured current in mA"""
        return self.data['actual_voltage'] / 500 + random.normalvariate(0,1)


    def ramp(self, new_voltage):
        while (abs(self.data['actual_voltage'] - new_voltage) >= 10):
            if (self.data['actual_voltage'] - new_voltage < 0):
                self.data['actual_voltage'] += 12
            else:
                self.data['actual_voltage'] -= 12
            time.sleep(0.05)

    def _ramp_thread(self, new_voltage) -> None:
        """ 
        Creates a thread to ramp up/down voltage without blocking the program.
        """
        self._ramping = True
        def ramp_sub():
            self.ramp(new_voltage)
            self._log(f"Target voltage met")
            self._ramping = False
        threading.Thread(target=ramp_sub, daemon=True).start()



    def _set_target(self, new_target_voltage) -> None:
        """
        Define a new target voltage for the OM. If the OM is not busy and the target is not close to the current voltage, it will ramp up/down to meet the target.
        """
        # ==== Security checks ====
        if (new_target_voltage > self.max_voltage):
            self._log(f"Can not set the input target voltage (value too high (max = {self.max_voltage}))")
            return
        if (new_target_voltage < self.min_voltage):
            self._log(f"Can not set the input target voltage (value too low (min = {self.min_voltage}))")
            return
        if (self.data['power'] == False): # check if OM is on
            self._log(f"Can not set a new target voltage (currently off)")
            return
        if self._ramping:          # check if OM is ramping
            self._log(f"Can not set a new target voltage (currently ramping)")
            return
        
        self.data['target_voltage'] = new_target_voltage
        self._log(f"Set new target voltage")
        self._ramp_thread(self.data['target_voltage'])

        
    def _turn_on(self) -> None:
        """
        Turn on the optical module. Once on, the OM will ramp up to the target voltage.
        """
        if self._ramping:
            self._log(f"Can not turn on (currently ramping)")
            return
        
        self._log(f"Turning ON")

        self.data['power'] = True
        self._log(f"Correctly turned ON")

        self._ramp_thread(self.data['target_voltage'])
        

    def _turn_off(self) -> None:
        """
        Ramp down the voltage to the minimum, then turn off the optical module.
        """
        if self._ramping:
            self._log(f"Can not turn off (currently ramping)")
            return
        
        self._log(f"Turning OFF")

        def turn_off_ramp():
            # First ramp down the voltage to the minimum.
            self.ramp(self.min_voltage)
            self._ramping = False

            self.data['power'] = False
            self._log(f"Correctly turned OFF")

        self._ramping = True
        threading.Thread(target=turn_off_ramp, daemon=True).start()

