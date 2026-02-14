from labterm import Instrument
import subprocess
import threading

        
class ServerTester(Instrument):
    """
    This object is responsible for pinging a single server address and storing its status. The status is contained in the ``online`` key of the ``data`` dictionary.

    Args:
        address (str): The ip address of the associated server
    """
    def __init__(self, channel, address = ''):
        super().__init__(channel)
        self.address = address
        self.data = {
            'online' : False
        }
    
    def _log(self, message):
        if self.logger:
            self.logger(f"{self.address}: {message}")
    
    def update_data(self):
        def ping_ip():
            "Pings the ip address associated with the server and sets the online status of the object based on the output"
            try:
                self._log(f"Pinging")
                output = subprocess.run(["ping", "-c", "1", self.address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if output.returncode == 0:
                    self.data['online'] = True
                else:
                    self.data['online'] = False
            except subprocess.CalledProcessError:
                # self._log(f"Error")
                self.data['online'] = False

        threading.Thread(target=ping_ip, daemon=True).start()

    def action(self, action_id, *args):
        "No action is associated with this instrument yet."
        pass
    