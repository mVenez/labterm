import curses
import time
import threading
import queue

from .dashboard_item import *
from .instrument import Instrument


class Dashboard:
    """
    Curses dashboard that displays `DashboardItem`s and polls `Instrument`s.

    The Dashboard runs a background thread to periodically call `Instrument.update_data()`
    and places new values into an internal queue that the main drawing loop consumes.

    Args:
        screen: curses screen object supplied by `curses.wrapper`.
        data_update_interval (float): In seconds, interval between instrument polls
        cycle (bool): Whether the grid allows cycling, i.e. navigating between the first and the last element of a line/column.
        header (str): A string continuously printed on the top left of the dashboard.
        show_time (bool): Whether to show the current time on the top of the dashboard.
        show_log (bool): Whether to show the last `max_log_messages` logs at the bottom of the dashboard.
        show_controls (bool): Whether to show the controls help text (`controls_text`) in a section of the dashboard.
        controls_text (list[str] | None): The text detailing the dashboard controls.
        grid_start (tuple[int,int]): The position the item selector starts in at the launch of the program.
        max_log_messages (int): Maximum number of log messages to be shown at once.

    Attributes:
        _instruments (dict[int, Instrument]): Instruments keyed by channel.
        _items (list[DashboardItem]): All dashboard items.
        _running (bool): True while dashboard main loop is running.

    Threading / lifecycle:
        - `Dashboard.__init__` starts a daemon thread that runs `_update_data_loop`.
        - `run()` is the main thread's drawing loop; it consumes the data queue.
        - `update_data` exceptions are caught and logged; ensure actions and updates are thread-safe where necessary.

    Example:
        >>> def main(stdscr):
        ...     dash = Dashboard(stdscr, header="LabTerm example")
        ...     dash.add_instrument(MyInstrument(channel=0))
        ...     dash.add_item(MyDashboardItem(...))
        ...     dash.run()...   
        ... if __name__ == '__main__':
        ...     import curses
        ...     curses.wrapper(main)

    """
    DEFAULT_CONTROLS = [
                    "↑/↓/←/→ - Navigate items               i - Invert colors",
                    "Enter - Toggle switch / Edit value     Numbers - Enter values (when editing)",
                    "Esc - Cancel edit                      q - Quit"
                    ]
    
    def __init__(
        self, 
        screen,
        data_update_interval: float = 0.3,
        cycle: bool = True, 
        header: str = "",
        show_time: bool = True,
        show_log: bool = True,
        show_controls: bool = True,
        controls_text: list[str] = None,
        grid_start: tuple[int, int] = (0, 0),
        max_log_messages: int = 6
    ) -> None:
        self._screen = screen


        # Navigation state 
        self._current_grid_x: int = grid_start[0]
        self._current_grid_y: int = grid_start[1]
        self._cycle: bool = cycle   # whether to cycle when at the end of the grid or not

        # Dashboard mode tracking
        self._running = True
        self._editing = False    # keeps track if the user is editing or not
        self._data_update_interval = data_update_interval  # [s], how often to update data

        # Display options
        self._header = header
        self._show_time = show_time
        self._show_log = show_log
        self._show_controls = show_controls
        self._max_log_messages= max_log_messages
        self._controls_text = controls_text or self.DEFAULT_CONTROLS

        # Log system
        self._log_messages: list[str] = []

        # Dashboard data structures
        self._instruments: dict[int, Instrument] = {}
        self._items: list[DashboardItem] = []

        # Initialize curses settings
        curses.curs_set(0)  # Hide cursor
        self._screen.nodelay(True)  # Non-blocking input
        self._screen.timeout(100)  # 100ms timeout for getch()
        
        self._inverted_colors: bool = False
        self._init_colors()
        
        # Start data update queue and thread 
        self._data_queue: queue.Queue = queue.Queue()
        self._data_thread = threading.Thread(
            target=self._update_data_loop, daemon=True
        )
        self._data_thread.start()
    

    def add_instruments(self, *instruments: Instrument) -> None:
        """
        Add one or more instruments to the dashboard.

        Each instrument is connected to the dashboard's logger and registered
        by its channel ID. Instruments with duplicate channel IDs will overwrite previous ones.

        Args:
            *instruments: Variable number of Instrument instances to add.
        """
        for new in instruments:
            new.logger = self._log
            self._instruments.update({new.channel : new})
    
    def add_items(self, *items : DashboardItem) -> None:
        """
        Add one or more dashboard items to the display.

        Items are drawn in the order they are added. Navigable items form a grid
        based on their xgrid and ygrid coordinates.

        Args:
            *items: Variable number of DashboardItem instances to add.
        """
        for new in items:
            self._items.append(new)

    def cycle(self, cycle: bool = True):
        """
        Sets whether to cycle when at the end of the navigable grid or not.
        """
        self._cycle = cycle

    def run(self):
        """
        Main dashboard loop:
            1 - Checks if the data queue contains updates for the values of the dashboard items, and applies the updates
            2 - Clears the window
            3 - Draws all the items, the decorators (header + instructions) and the logs
            4 - Handles user input, separating between editing and navigation
        """
        try:
            while self._running:
                # Apply updates from queue
                while not self._data_queue.empty():
                    updated_items = self._data_queue.get() # removes and returns items from the queue
                    for item, new_value in updated_items:
                        item.value = new_value

                
                self._screen.erase()
                
                # Draw all items, logs and decorators
                self._draw_header()

                for i, item in enumerate(self._items):
                    selected = (item.xgrid == self._current_grid_x and item.ygrid == self._current_grid_y) if item.navigable else False
                    item.draw(self._screen, selected=selected)
                
                if self._show_controls:
                    self._draw_controls()
                if self._show_log:
                    self._draw_log()
                
                # Update display
                self._screen.refresh()
                
                # Handle input
                if not self._handle_input():
                    break

                time.sleep(0.05)
        finally:
            self._running = False

    def set_header(self, header: str) -> None:
        """Sets the program header, printed on the top left."""
        self._header = header

    def set_max_logs(self, max_number: int) -> None:
        """Sets the maximum number of log messages displayed at once at the bottom of the screen"""
        self._max_log_messages = max_number

    def set_update_interval(self, interval: float) -> None:
        """Set every how many seconds the program gathers data from the instruments to update the dashboard"""
        self._data_update_interval = interval

    def show_controls(self, show:bool) -> None:
        """Sets whether the dashboard controls are printed or not on the dashboard."""
        self._show_controls = show

    def show_log(self, show:bool) -> None:
        """Sets whether the log messages are printed or not on the dashboard."""
        self._show_log = show

    def _update_data_loop(self) -> None:
        """
        Background loop that polls instruments and queues updated values.

        Behavior:
            - Iterates over `self._items` and, if an item is bound to an instrument
              channel, calls `instrument.update_data()` and queues the new value.
            - Puts a list of `(item, new_value)` tuples into `self._data_queue`.
            - Sleep interval controlled by `self._data_update_interval`.

        Notes:
            - Implementations of `Instrument.update_data` should be safe to call
              from a separate thread.
            - Consumers (the main thread) should only access item.value from the
              main thread to avoid race conditions.

        Raises:
            Exceptions are caught and logged via `self._log`.
        """
        while self._running:
            try:
                updated_items = []
                # Update dashboard items with data from instruments
                for item in self._items:
                    if (item.channel is not None and item.data is not None):
                        # first update info contained in instrument object
                        instrument = self._instruments[item.channel]
                        instrument.update_data() 

                        # grab the updated value for the quantity/state the item manages
                        new_value = instrument.data[item.data]

                        # form a list with all the updates
                        if new_value is not None:
                            updated_items.append((item,new_value))

                # finally, put the list of all incoming updates in the data queue, to be processed by `self.run()`
                self._data_queue.put(updated_items) # put list in queue
                time.sleep(self._data_update_interval) 
                
            except Exception as e:
                # Handle any communication errors with instruments
                self._log(f"Error updating instrument data: {e}")
                time.sleep(1.0)

    def _log(self, message: str) -> None:
        """
        Add a timestamped message to the log. 
        Only the max_log_messages last messages are displayed.
        """
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self._log_messages.append(full_message)
        
        # Keep only the most recent messages
        if len(self._log_messages) > self._max_log_messages:
            self._log_messages.pop(0)
    
    def _draw_header(self):
        """Draw the dashboard header"""
        window_height, window_width = self._screen.getmaxyx()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        start_x_time = int((window_width // 2) - (len(timestamp) // 2) - len(timestamp) % 2)

        self._screen.addstr(0, 0, self._header, curses.A_BOLD | curses.color_pair(1))
        if self._show_time:
            self._screen.addstr(0, start_x_time, timestamp, curses.color_pair(1))

    def _draw_log(self):
        """Draw the last logged messages on the bottom of the screen."""
        window_height, window_width = self._screen.getmaxyx()

        self._draw_sectiontitle("Log", window_height - self._max_log_messages - 1)
        for i, message in enumerate(self._log_messages):
            self._screen.addstr(window_height - self._max_log_messages + i, 0, message, curses.color_pair(1))
    
    
    def _draw_controls(self):
        """Draw control instructions"""
        window_height, window_width = self._screen.getmaxyx()
        start_y = window_height - self._max_log_messages - len(self._controls_text) - 1

        self._draw_sectiontitle("Controls", start_y - 1)
        for i, line in enumerate(self._controls_text):
            self._screen.addstr(start_y + i, 0, line, curses.color_pair(1))
    
    def _draw_sectiontitle(self, title:str, row:int, title_position: int = 4):
        "Draws a line at `y=row`, containing string title at `x=title_position`"
        window_height, window_width = self._screen.getmaxyx()
        self._screen.hline(row, 0, curses.ACS_HLINE, title_position-1, curses.color_pair(1))
        self._screen.addstr(row, title_position, title, curses.A_BOLD | curses.color_pair(1))
        self._screen.hline(row, title_position + len(title)+1, curses.ACS_HLINE, window_width, curses.color_pair(1))

    def _init_colors(self):
        """Initialises the curses colors used across the dashboard. Checks if the inverted colors setting is enabled and adjusts the colors."""
        curses.start_color()
        if self._inverted_colors:
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Default text
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Selected
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)  # ON state
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)    # OFF state
            curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_WHITE) # Editable
        else:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Default text
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # ON state
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # OFF state
            curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Editable


    # ============================ user input handling =========================== #
    def _get_item_at_grid(self, x: int, y: int) -> Optional[tuple[int, DashboardItem]]:
        """
        Get item at grid position.
    
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            
        Returns:
            (index, item): or None if not found
        """
        for idx, item in enumerate(self._items):
            if item.navigable and item.xgrid == x and item.ygrid == y:
                    return idx, item
        return None

    def _handle_input(self) -> bool:
        """
        Handle general user input, distinguishing between navigation commands and item edit commands.
        """
        try:
            key = self._screen.getch()
            if key == -1:  # No input
                return True
                
            if self._editing:
                return self._handle_edit_input(key)
            else:
                return self._handle_navigation_input(key)
                
        except curses.error:
            return True
    
    def _handle_edit_input(self, key):
        """Handle input during value editing (numerical, not on/off switches)"""
        idx, item = self._get_item_at_grid(self._current_grid_x, self._current_grid_y)

        end_edit, value = item.handle_edit_key(key)
        if end_edit:
            self._editing = False
            item.exit_edit()
            if value is not None:
                instrument = self._instruments[item.channel]
                instrument.action(item.action, value)
            
        return True
    
    def _handle_navigation_input(self, key):
        """Handle navigation input and turning switches on/off"""
        navigable_items = [item for item in self._items if item.navigable]
        if not navigable_items:
            # Handle global keys even without navigable items
            if key == ord('i'):
                self._inverted_colors = not self._inverted_colors
                self._init_colors()
                self._screen.bkgd(' ', curses.color_pair(1))

            elif key == ord('q'):
                return False
            return True
        
        max_x = max(item.xgrid for item in navigable_items)
        max_y = max(item.ygrid for item in navigable_items)

        # Navigation
        if key == curses.KEY_UP:
            if self._cycle:
                self._current_grid_y = (self._current_grid_y - 1) % (max_y + 1)
            elif self._current_grid_y > 0:
                self._current_grid_y -= 1
            
        elif key == curses.KEY_DOWN:
            if self._cycle:
                self._current_grid_y = (self._current_grid_y + 1) % (max_y + 1)
            elif self._current_grid_y < max_y:
                self._current_grid_y += 1
            
        elif key == curses.KEY_LEFT:
            if self._cycle:
                self._current_grid_x = (self._current_grid_x - 1) % (max_x + 1)
            elif self._current_grid_x > 0:
                self._current_grid_x -= 1
        
        elif key == curses.KEY_RIGHT:
            if self._cycle:
                self._current_grid_x = (self._current_grid_x + 1) % (max_x + 1)
            elif self._current_grid_x < max_x:
                self._current_grid_x += 1

        # Interaction
        elif key == ord('\n') or key == 10:  # Enter
            idx, item = self._get_item_at_grid(self._current_grid_x, self._current_grid_y)
            
            if item.editable:
                self._editing = True
                item.enter_edit()

            else: # non editable items immediately execute the associated action
                if item.channel is None or item.action is None: 
                    self._log(
                        f"Warning: Item at ({item.xgrid}, {item.ygrid}) "
                        f"missing channel or action"
                    )
                else:
                    instrument = self._instruments[item.channel]
                    if instrument:
                        instrument.action(item.action)
                    else:
                        self._log(f"No instrument found for channel {item.channel}")


        elif key == ord('i'):
            self._inverted_colors = not self._inverted_colors
            self._init_colors()
            self._screen.bkgd(' ', curses.color_pair(1))

        elif key == ord('q'):
            return False
        return True
