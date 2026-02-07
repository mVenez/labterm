import curses
from typing import Any, Optional, Literal
from abc import ABC, abstractmethod


class DashboardItem(ABC):
    """
    An item drawable on the dashboard, associated with a measured quantity or a state of a specific instrument.

    Args:
        x: x position in dashboard. 
            The way this value translates to a column of the terminal is decided by xycoords
        y: y position in dashboard (higher y corresponds to a lower position). 
            The way this value translates to a row of the terminal is decided by xycoords
        xgrid (int): If navigable, determines the x position of the item on the navigable grid
        ygrid (int): If navigable, determines the y position of the item on the navigable grid
        channel (int): A number associating the items with an instrument.
            Enter a channel equal to the one set for the desired instrument for the two to communicate. 
        data (str): The specific data associated with the item, obtained by the instrument of corresponding channel.
            Must be one of the keys of the instrument data dict.
            The item will continuosly update the data in the way described by the instrument update_data() method.
        action (str): The action to carry out when selecting the item.
            Must be one of the actions foreseen by the instrument action() method.
        text_before (str): A string to be printed before the main item text
        text_after (str): A string to be printed after the main item text
        value: The main content of the item, contains the value (or data structure) to be printed, updated, or modified as wished.
        decimals (int): If displaying floats, determines how many decimals to show.
        xycoords (Literal["prop", "int"]): Determines how to translate the x,y values into terminal screen coordinates 
            - prop: coordinate system of the axes, x,y are floats between 0 and 1, (0, 0) is top left, and (1, 1) is top right. 
            - int: exact column and row position, x,y, are ints.
        halign (Literal["left", "center", "right"]): horizontal alignment of the item with respect to the x,y coordinates
        valign (Literal["top", "center", "bottom"]): vertical alignment of the item with respect to the x,y coordinates
        xoffset (int): number of columns, horizontal offset with respect to the x position.
            Useful to group together groups of items.
        yoffset (int): number of rows, vertical offset with respect to the y position.
            Useful to group together groups of items.
    """
    navigable: bool = False
    editable: bool = False

    def __init__(
        self, 
        x, y,
        xgrid: Optional[int] = None,
        ygrid: Optional[int] = None, 
        channel: Optional[int] = None,
        data: Optional[str] = None,
        action: Optional[str] = None,
        text_before: str = '',
        text_after: str = '',
        value: Optional[Any] = None,
        decimals: int = 2,
        xycoords: Literal["prop", "int"] = "prop", 
        halign: Literal["left", "center", "right"] = "left",
        valign: Literal["top", "center", "bottom"] = "top",
        xoffset: int = 0,
        yoffset: int = 0
    ) -> None:
        self.x = x
        self.y = y
        self.xgrid = xgrid
        self.ygrid = ygrid
        self.channel = channel
        self.data = data
        self.action = action
        self.value = value
        self.text_before = text_before
        self.text_after = text_after
        self.decimals = decimals
        self.xycoords = xycoords
        self.halign = halign
        self.valign = valign
        self.xoffset = xoffset
        self.yoffset = yoffset

    @abstractmethod
    def draw(self, screen, selected: bool = False) -> None:
        """
        Draw the item on the screen
        """
        if (self.x < 0 or self.y < 0):
            raise ValueError("x and y positions must be non-negative")
        pass


    def handle_edit_key(self, key) -> tuple[bool, Optional[float]]:
        """
        Determines what happens when a key is pressed while editing an item.
        Returns a tuple (exit_editing, commit_value). 

        If `exit_editing=True` the dashboard will get out of editing mode, and the item `action` will be called with the `commit_value` returned.
        If `commit_value=None` the dahsboard will cancel the edit.
        """
        pass
    
    def enter_edit(self):
        """
        This method is called when an item enters editing mode.
        """
        pass

    def exit_edit(self):
        """
        This method is called when an item enters editing mode.
        """
        pass

    def _calculate_position(self, screen, text_length: int = 0):
        """
        Calculate the actual x, y position to draw the item on, based on coordinate system, horizontal and vertical alignment.
        
        Args:
            screen: The curses window object
            text_length: Length of the considered text (for alignment calculations)
        
        Returns:
            tuple: (xpos, ypos) - the calculated screen coordinates
        """
        window_height, window_width = screen.getmaxyx()
        
        # Convert coordinates to absolute screen positions
        if self.xycoords == "int":
            xpos, ypos = int(self.x), int(self.y)
        elif self.xycoords == "prop":
            xpos, ypos = int(self.x * window_width), int(self.y * window_height)
        else:
            raise ValueError(
                f"Invalid coordinate system '{self.xycoords}'. "
                f"Must be 'int' or 'prop'."
            )
        
        # Apply horizontal alignment
        if self.halign == "left":
            pass
        elif self.halign == "center":
            xpos -= text_length // 2
        elif self.halign == "right":
            xpos -= (text_length - 1)
        else:
            raise Exception("DashboardItem: Unknown horizontal alignment blabla")
        
        # TODO: Apply vertical alignment
        
        # Apply offsets
        xpos += self.xoffset
        ypos += self.yoffset
        
        # Clamp to valid screen boundaries
        if xpos < 0:
            xpos = 0
        if ypos < 0:
            ypos = 0
        
        return xpos, ypos


class Label(DashboardItem):
    """
    A static, non-navigable and non-editable item, without associated data or action.

    Args:
        x: x position in dashboard. 
            The way this value translates to a column of the terminal is decided by xycoords
        y: y position in dashboard (higher y corresponds to a lower position). 
            The way this value translates to a row of the terminal is decided by xycoords
        text (str): The text to be printed
    """
    def __init__(self, x, y, text: str, **kwargs):
        super().__init__(x, y, **kwargs)
        self.value = text

    def draw(self, screen, **kwargs):
        text = self.text_before + self.value + self.text_after
        xpos, ypos = self._calculate_position(screen, len(self.value))
        screen.addstr(ypos, xpos, text, curses.A_BOLD | curses.color_pair(1))



class Switch(DashboardItem):
    """
    A dynamic, navigable, non-editable item, which alternates between two possible states.

    Args:
        x: x position in dashboard. 
            The way this value translates to a column of the terminal is decided by xycoords
        y: y position in dashboard (higher y corresponds to a lower position). 
            The way this value translates to a row of the terminal is decided by xycoords
        xgrid (int): If navigable, determines the x position of the item on the navigable grid
        ygrid (int): If navigable, determines the y position of the item on the navigable grid
        channel (int): A number associating the items with an instrument.
            Enter a channel equal to the one set for the desired instrument for the two to communicate. 
        data (str): The specific data associated with the item, obtained by the instrument of corresponding channel.
            Must be one of the keys of the instrument data dict.
            Must be of boolean nature.
            The item will continuosly update the data in the way described by the instrument update_data() method.
        action (str): The action to carry out when the item switches between the two possible states.
            Must be one of the actions foreseen by the instrument action() method.
        initial_value (bool): The initial value stored in the item.
    """
    navigable = True
    editable = False
    def __init__(
        self, 
        x, y, 
        xgrid: int, ygrid: int,
        channel: int, 
        data: str, 
        action: str, 
        initial_value: bool = False, 
        text:tuple[str, str] = ("ON", "OFF"),
        **kwargs
    ) -> None:
        super().__init__(
            x, y, 
            xgrid=xgrid, ygrid=ygrid, 
            channel=channel, data=data, action=action,
            value=initial_value,
            **kwargs
        )
        self.text = text
    
    def draw(self, screen, selected):
        state_text = f"[{self.text[0]}]" if self.value else f"[{self.text[1]}]"
        text = self.text_before + state_text + self.text_after
        color = curses.color_pair(3) if self.value else curses.color_pair(4)
        xpos, ypos = self._calculate_position(screen, len(text))
        if selected:
            color |= curses.A_REVERSE
        screen.addstr(ypos, xpos, text, color)


class Readonly(DashboardItem):
    """
    A dynamic, non-navigable, non-editable item, which updates and prints data associated with an instrument.

    Args:
        x: x position in dashboard. 
            The way this value translates to a column of the terminal is decided by xycoords
        y: y position in dashboard (higher y corresponds to a lower position). 
            The way this value translates to a row of the terminal is decided by xycoords
        xgrid (int): If navigable, determines the x position of the item on the navigable grid
        ygrid (int): If navigable, determines the y position of the item on the navigable grid
        channel (int): A number associating the items with an instrument.
            Enter a channel equal to the one set for the desired instrument for the two to communicate. 
        data (str): The specific data associated with the item, obtained by the instrument of corresponding channel.
            Must be one of the keys of the instrument data dict.
            The item will continuosly update the data in the way described by the instrument update_data() method.
        initial_value (bool): The initial value stored in the item.
    """
    def __init__(self, 
                 x, y,
                 channel: int, data: str,
                 initial_value = 0.,
                 **kwargs
                 ):
        super().__init__(
            x, y, 
            channel=channel, data=data, 
            value=initial_value, 
            **kwargs
        )

    def draw(self, screen, **kwargs):
        if self.value is None:
            value_str = "--"
        else:
            value_str = f"{self.value:.{self.decimals}f}"
        text = self.text_before + value_str + self.text_after
        xpos, ypos = self._calculate_position(screen, len(text))
        screen.addstr(ypos, xpos, text)


class Editable(DashboardItem):
    """
    A dynamic, navigable, editable item, which sets, updates and prints data associated with an instrument.

    Args:
        x: x position in dashboard. 
            The way this value translates to a column of the terminal is decided by xycoords
        y: y position in dashboard (higher y corresponds to a lower position). 
            The way this value translates to a row of the terminal is decided by xycoords
        xgrid (int): If navigable, determines the x position of the item on the navigable grid
        ygrid (int): If navigable, determines the y position of the item on the navigable grid
        channel (int): A number associating the items with an instrument.
            Enter a channel equal to the one set for the desired instrument for the two to communicate. 
        data (str): The specific data associated with the item, obtained by the instrument of corresponding channel.
            Must be one of the keys of the instrument data dict.
            The item will continuosly update the data in the way described by the instrument update_data() method.
        action (str): The action to carry out when selecting the item.
            Must be one of the actions foreseen by the instrument action() method.
        initial_value (bool): The initial value stored in the item.
    """
    navigable = True
    editable = True
    def __init__(self, 
                 x, y,
                 xgrid: int, ygrid: int,
                 channel: int, data: str, action: str,
                 initial_value = 0.,
                 **kwargs
                 ):
        super().__init__(
            x, y, 
            xgrid=xgrid, ygrid=ygrid, 
            channel=channel, 
            data=data, 
            action=action, 
            value=initial_value, 
            **kwargs
        )

        self._edit_buffer = initial_value
        self._editing = False

    def draw(self, screen, selected: bool):
        value_str = f"{self.value:.{self.decimals}f}"
        text = self.text_before + value_str + self.text_after
        xpos, ypos = self._calculate_position(screen, len(text))
        color = curses.color_pair(1)
        if self._editing:
            text = str(self._edit_buffer)
            color = curses.color_pair(5)
            text = '>' + text + '_'
        if selected:
            color |= curses.A_REVERSE
        screen.addstr(ypos, xpos, text, color)
    
    def enter_edit(self):
        self._editing = True
        self._edit_buffer = ''

    def exit_edit(self):
        self._editing = False

    def handle_edit_key(self, key) -> tuple[bool, Optional[float]]:
        if key == 27:  # Escape
            return (True, None)
            
        elif key == ord('\n') or key == 10:  # Enter
            try:
                self.value = float(self._edit_buffer)
                    
                return (True, self.value)
            except ValueError:
                # Invalid input, cancel edit
                self._edit_buffer = self.value
                return (True, 0)
                
        elif key == 127 or key == curses.KEY_BACKSPACE:  # Backspace
            self._edit_buffer = self._edit_buffer[:-1]
            return (False, 0)
            
        elif chr(key).isdigit() or chr(key) in '.-':
            self._edit_buffer += chr(key)
            return (False, 0)

        else:
            return (False, None)
        
class Light(DashboardItem):
    """
    A dynamic, non-navigable, non-editable item, which updates boolean data associated with an instrument and represents it with a green (True) or red (False) circle in a single character.

    Args:
        x: x position in dashboard. 
            The way this value translates to a column of the terminal is decided by xycoords
        y: y position in dashboard (higher y corresponds to a lower position). 
            The way this value translates to a row of the terminal is decided by xycoords
        xgrid (int): If navigable, determines the x position of the item on the navigable grid
        ygrid (int): If navigable, determines the y position of the item on the navigable grid
        channel (int): A number associating the items with an instrument.
            Enter a channel equal to the one set for the desired instrument for the two to communicate. 
        data (str): The specific data associated with the item, obtained by the instrument of corresponding channel.
            Must be one of the keys of the instrument data dict.
            The item will continuosly update the data in the way described by the instrument update_data() method.
        initial_value (bool): The initial value stored in the item.
    """
    def __init__(self, 
                 x, y,
                 channel: int, data: str,
                 initial_value = False,
                 **kwargs
                 ):
        super().__init__(
            x, y, 
            channel=channel, data=data, 
            value=initial_value, 
            **kwargs
        )

    def draw(self, screen, **kwargs):
        if self.value is None:
            value_str = "-"
        else:
            value_str =  "●"
        text = self.text_before + value_str + self.text_after
        xpos, ypos = self._calculate_position(screen, len(text))
        if self.value:
            screen.addstr(ypos, xpos, text, curses.color_pair(3))
        else:
            screen.addstr(ypos, xpos, text, curses.color_pair(4))
