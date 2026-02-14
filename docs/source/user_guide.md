# User Guide

This page contains all you need to know about LabTerm and how to use it to create interactive graphical interfaces.
While reading this, check out the **examples** in the repository! They're the easiest way to understand how LabTerm works.

## Creating a Dashboard from scratch
To create your own dashboard you need to:
1. Define one or more subclasses of `Instrument`, which represent the instrument/system you want to interface on. The subclass must contain
    - A `data` dictionary, containing the data values which are monitored/controlled by the instrument.
    - An `update_data()` method, which determines what to do when the dashboard asks the instrument to update its data.
    - An `action()` method which defines how to handle actions requested from the `Dashboard` (for example pressing enter on a dashboard item could do something)
2. In your main script `import labterm`, initialise the `Dashboard` with the settings you prefer and connect it to the instruments.
3. Define and add to the dashboard the various `DashboardItem` you want: these are the items drawn on the dashboard, associated with a measured quantity or a state of a specific instrument, which can take several forms and functions.

### Instruments
(WIP)
### Dashboard
(WIP)
### Dashboard Items
(WIP)

## Custom Dashboard Items
(WIP)
