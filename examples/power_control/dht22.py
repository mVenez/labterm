from src.instrument import Instrument
from src.rpi_lib import *
import adafruit_dht
import board

class DHT22(Instrument):
    """
    DHT22 temperature and humidity sensor
    """
    def __init__(self, channel):
        super().__init__(channel)
        self.data = {
            'temperature' : 0.0,
            'humidity' : 0.0
        }
        self.sensor = adafruit_dht.DHT22(board.D6)


    def action(self, id: str, *args):
        "For now, no action tied to the DHT22."
        pass
    

    def update_data(self):
        """Called by the Dashboard. Updates all data relative to Battery and stores it in self.data."""
        try:
            self.data['temperature'] = self.sensor.temperature
            self.data['humidity'] = self.sensor.humidity
        except Exception as exceptionmsg:
            self._log(str(exceptionmsg))
        
    def _log(self, message: str):
        """
        Send a message through the set logger function.
        """
        if self.logger:
            self.logger(f"DHT22: {message}")
