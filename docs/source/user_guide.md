# User Guide

This page contains all you need to know about LabTerm and how to use it to create interactive graphical interfaces.
While reading this, check out the **examples** in the repository! They're the easiest way to understand how LabTerm works.

## Creating a Dashboard from scratch
To create your own dashboard you need to:
1. Define one or more subclasses of [Instrument](instrument.rst), which represent the instrument/system you want to interface on. The subclass must contain
    - A `data` dictionary, containing the data values which are monitored/controlled by the instrument.
    - An `update_data()` method, which determines what to do when the dashboard asks the instrument to update its data.
    - An `action()` method which defines how to handle actions requested from the [Dashboard](dashboard.rst) (for example pressing enter on a dashboard item could do something)
2. In your main script `import labterm`, initialise the [Dashboard](dashboard.rst) with the settings you prefer and connect it to the instruments.
3. Define and add to the dashboard the various [DashboardItem](dashboard_item.rst) you want: these are the items drawn on the dashboard, associated with a measured quantity or a state of a specific instrument, which can take several forms and functions.

### Instruments
An [Instrument](instrument.rst) contains all the logic necessary to store, update and modify data regarding a specific part of your setup/system.
An instrument could be the Python interface for a digital multimeter, or the GPIO pins of a Raspberry Pi, or the pointing mechanism ensemble of an antenna (composed of several sensors and motors), but also something completely abstract such as a scheduler for some program or a manager for TCP communication.

The dashboard launches the data update routine simultaneously for each separate instrument.
As such, it's a good idea to keep instruments which are physically distinct or relate to different parts of your system in different subclasses, to allow them to operate at the same time.

Each [Instrument](instrument.rst) subclass must contain
- a `data` dictionary. This is where you store values which need to be accessible by the dashboard items and can change in time, either as part of the data update of the instrument, or because a dashboard item modified them.
- An `update_data()` method, which determines what to do when the dashboard asks the instrument to update its data.
- An `action()` method which defines how to handle actions requested from the [Dashboard](dashboard.rst) (for example pressing enter on a dashboard item could do something).


### Dashboard
The Dashboard contains the main drawing and interacting logic of the program and is responsible for coordinating instruments, dashboard items and the user input.

The user is responsile for adding to the dashboard
1. the instruments he has defined and instantiated ({py:func}`add_instruments() <labterm.dashboard.Dashboard.add_instruments>`).
2. the various dashboard items he wants the dashboard to consist of ({py:func}`add_items() <labterm.dashboard.Dashboard.add_items>`).

The dashboard will then take care of 
- Running the background threads which keep the data of the instruments updated
- Monitoring the user input and acting on it, by invoking the actions assigned to the items
- Running the drawing loop which reflects these changes

The behaviour and appearance of the dashboard is customizable:
```{eval-rst}

.. autosummary::
   :nosignatures:

   labterm.dashboard.Dashboard.set_header
   labterm.dashboard.Dashboard.set_max_logs
   labterm.dashboard.Dashboard.set_update_interval
   labterm.dashboard.Dashboard.show_controls
   labterm.dashboard.Dashboard.show_log
   labterm.dashboard.Dashboard.cycle
```

### Dashboard Items
The dashboard items define the appearance and functionality of your dashboard.
There are several types available:

```{eval-rst}
.. currentmodule:: labterm.dashboard_item

.. rubric:: Static decorators

Non-interactive visual elements.

.. autosummary::
   :nosignatures:

   Header
   Label
```

```{eval-rst}
.. currentmodule:: labterm.dashboard_item

.. rubric:: Live displays

Read-only items that continuously update from instrument data. Must be associated to a `channel` (to connect to the right instrument) and a `data` (one of the keys of the instrument data dict).

.. autosummary::
   :nosignatures:

   Readonly
   Light
```

```{eval-rst}
.. currentmodule:: labterm.dashboard_item

.. rubric:: Interactive controls

User-operable items that send commands to instruments. Must be associated to a `channel`, an `action` (Must be one of the actions foreseen by the instrument action() method), and optionally to some `data`.

.. autosummary::
   :nosignatures:

   Button
   Switch
   Editable
```

All interactive controls participate in keyboard navigation (arrow keys to
select, Enter to activate). Static decorators and live displays do not.

#### Dashboard items settings
See the {py:class}`base class <labterm.dashboard_item.DashboardItem>` for all items to check which settings are shared among all items.
Among these:
- The position `x`, `y`
- The offset in lines with respect to the position `xoffset`, `yoffset`
- The position in the navigable grid `xgrid`, `ygrid`
- The coordinate system `xycoords`
- Some text to be printed before or after the main item text (`text_before` and `text_after`)
- The horizontal and vertical print alignment with respect to the x,y coordinates (`halign`, `valign`)
- the number of decimals to print if numerical (`decimals`)



## Custom Dashboard Items
It's easy to define custom items if the ones contained in the library are not suited for a specific feature you want in your dashboard.

If you're not sure how to draw something on the dashboard you can check the [curses documentation](https://docs.python.org/3/library/curses.html#module-curses).

### Minimal example
```python
class MinimalItem(lt.DashboardItem):
"""
A simple dashboard item whose 'value' is constantly updated and printed.
"""
def __init__(self, x, y, channel, data, **kwargs):
   super().__init__(x, y, channel=channel, data=data, **kwargs)

   # self.value is updated by the dashboard based on the value received by the `update_data()` method of the Instrument for the `data` set for the item.
   self.value = "data_to_update_and_print"

def draw(self, screen: curses.window, **kwargs):
   """
   Draw the item based on its current value. 
   This is where you would define the way the item looks.
   """
   # Use the _calculate_position method to manage the horizontal and vertical alignment of the item 
   xpos, ypos = self._calculate_position(screen, self.value)
   
   lines = self.value.splitlines()

   for i, line in enumerate(lines):
         screen.addstr(ypos+i, xpos, line)

   # if you know the text is contained in a single line you can skip the for loop and simply use:
   # screen.addstr(ypos, xpos, line)
```

### Editable item
(WIP)
