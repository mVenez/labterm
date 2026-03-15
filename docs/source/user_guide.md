# User Guide

This page contains all you need to know about LabTerm and how to use it to create interactive graphical interfaces.
While reading this, check out the **examples** in the repository! They're the easiest way to understand how LabTerm works.

## Creating a Dashboard from scratch
To create your own dashboard you need to:
1. Define one or more subclasses of [Instrument](instrument.rst), which represent the instrument/system you want to interface on. The subclass must contain
    - A `data` dictionary, containing the data values which are monitored/controlled by the instrument.
    - An `update_data()` method, which determines what to do when the dashboard asks the instrument to update its data.
    - An `action()` method which defines how to handle actions requested from the [Dashboard](#dashboard.Dashboard) (for example pressing enter on a dashboard item could do something)
2. In your main script `import labterm`, initialise the [Dashboard](#dashboard.Dashboard) with the settings you prefer and connect it to the instruments.
3. Define and add to the dashboard the various [DashboardItem](dashboard_item.rst) you want: these are the items drawn on the dashboard, associated with a measured quantity or a state of a specific instrument, which can take several forms and functions.

### Instruments
An [Instrument](instrument.rst) contains all the logic necessary to store, update and modify data regarding a specific part of your setup/system.
An instrument could be the Python interface for a digital multimeter, or the GPIO pins of a Raspberry Pi, or the pointing mechanism ensemble of an antenna (composed of several sensors and motors), but also something completely abstract such as a scheduler for some program or a manager for TCP communication.

The dashboard launches the data update routine simultaneously for each separate instrument.
As such, it's a good idea to keep instruments which are physically distinct or relate to different parts of your system in different subclasses, to allow them to operate at the same time.

Each [Instrument](instrument.rst) subclass must contain
- a `data` dictionary. This is where you store values which need to be accessible by the dashboard items and can change in time, either as part of the data update of the instrument, or because a dashboard item modified them.
- An `update_data()` method, which determines what to do when the dashboard asks the instrument to update its data.
- An `action()` method which defines how to handle actions requested from the [Dashboard](#dashboard.Dashboard) (for example pressing enter on a dashboard item could do something).


### Dashboard
The Dashboard contains the main drawing and interacting logic of the program and is responsible for coordinating instruments, dashboard items and the user input.

The user is responsile for adding to the dashboard
1. the instruments he has defined and instantiated ({py:func}`add_instruments() <labterm.dashboard.Dashboard.add_instruments>`).
2. the various dashboard items he wants the dashboard to consist of ({py:func}`add_items() <labterm.dashboard.Dashboard.add_items>`).

The dashboard will then take care of 
- Running the background threads which keep the data of the instruments updated
- Monitoring the user input and acting on it, by invoking the actions assigned to the items
- Running the drawing loop which reflects these changes

The behaviour and appearance of the dashboard is highly customizable:
(WIP)

### Dashboard Items
(WIP)

## Custom Dashboard Items
(WIP)
