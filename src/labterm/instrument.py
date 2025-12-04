from abc import ABC, abstractmethod
from typing import Any, Callable, Optional


class Instrument(ABC):
    """
    Abstract base class for all instruments connected to the dashboard.

    Concrete subclasses must implement `update_data` and `action`. The Dashboard
    expects each instrument to expose a `data` dict and an optional `logger`
    callable.

    Args:
        channel (int): Unique channel id identifying the instrument.

    Attributes:
        data (dict[str, Any]): Live instrument data. Keys and value types are
            instrument-specific. Dashboard items update their values from this dictionary.
        logger (Optional[Callable[[str], None]]): Optional logging callback set
            by the `Dashboard` via `instrument.logger = self._log`.

    Example:
        >>> class MyInstrument(Instrument):
        ...     def __init__(self, channel):
        ...         super().__init__(channel)
        ...         self.data = {'voltage': None}
        ...
        ...     def update_data(self):
        ...         self.data['voltage'] = 3.3
    """

    def __init__(self, channel:int) -> None:
        self.channel = channel
        self.data: dict[str, Any] = {}
        self.logger: Optional[Callable[[str, None]]] = None


    def _log(self, message:str):
        """
        Send a message through the set logger function.
        """
        if self.logger:
            self.logger(f"Instrument {self.channel}: {message}")

    @abstractmethod
    def action(self, action_id:str, *args: Any) -> None:
        """Handle an action request from a `DashboardItem`.

        Implementations should perform the action or raise a clear exception.

        Args:
            action_id (str): Identifier for the requested action (e.g. "set_voltage").
            *args: Additional action arguments.

        Raises:
            ValueError: If arguments are invalid for the requested action.
            RuntimeError: If the action could not be completed.
        """
        pass

    @abstractmethod
    def update_data(self) -> None:
        """
        Refresh `self.data` with current instrument values.

        This method is called periodically from a Dashboard background thread.

        Raises:
            Exception: Propagate exceptions if communication fails; Dashboard will
            catch and log them.
        """
        pass
