import curses
import labterm as lt
import math

class AntennaPosition(lt.DashboardItem):
    """
    A dashboard item to visualize the current position of the antenna with a polar projection.
    """
    def __init__(self, x, y, channel, data, **kwargs):
        super().__init__(x, y, channel=channel, data=data, **kwargs)
        self.base_drawing = """\
      # # # # # 
    #           # 
  #               #
#                   #
#                   #
#                   #
#                   #
#                   #
  #               #
    #           # 
      # # # # # """
        # self.value is updated by the dashboard based on the instructions contained in the update_data() method of the Instrument for the specific data considered.
        self.value = (0,90)

    def draw(self, screen: curses.window, **kwargs):
        # Use the _calculate_position method to manage the horizontal and vertical alignment of the item 
        xpos, ypos = self._calculate_position(screen, self.base_drawing)
        
        lines = self.base_drawing.splitlines()
        nb_lines = len(lines)
        max_width = max(len(line) for line in lines)

        az, alt = self.value
        r = (90 - alt) / 90 * (min(max_width, nb_lines) / 2)

        x = round(max_width / 2 - 2 * r * math.sin(math.radians(az)) - 0.1)
        y = round(nb_lines / 2 + r * math.cos(math.radians(az)) - 0.1)
        x = max(0, min(max_width-1, x))
        y = max(0, min(nb_lines-1, y))

        lines[y] = lines[y][:x] + '*' + lines[y][x + 1:]

        for i, line in enumerate(lines):
            screen.addstr(ypos+i, xpos, line)
        
