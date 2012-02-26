from launchpad import Launchpad
from time_management import sequencer

class HomePad(object):
    
    def __init__(self):
        self.pad = Launchpad()
        #None indicates home screen
        self.active_column = None
        self.columns = []
        self.position_x = 0
        self.position_y = 0
        self.input_context = None
        
        sequencer.add(self)
    
    def add_column(self, column):
        self.columns.append(column)
        
    def _send_column_event(self, event):    
        column_num = event.get_column() + self.position_x
        row_num = event.get_row() + self.position_y
        
        if column_num >= len(self.columns): return
        column = self.columns[column_num]

        if event.is_a_push() and hasattr(column, "onColumnPush"):
            column.onColumnPush(row_num)
        elif event.is_a_release() and hasattr(column, "onColumnRelease"):
            column.onColumnRelease(row_num)
    
    def _send_focused_event(self, event):
        column = self.columns[self.active_column]
        if event.is_a_push() and hasattr(column, "onFocusedPush"):
            column.onFocusedPush(event)
        elif event.is_a_release() and hasattr(column, "onFocusedRelease"):
            column.onFocusedRelease(event)
    
    def _update_lights(self):
        if self.active_column is None:
            lights = []
            for column in self.columns[self.position_x:]:
                lights.extend(column.column_lights)
        else:
            lights = self.columns[self.active_column].focused_lights
        
        #fill the leftover spots 
        for i in range(len(lights), 64):
            lights.append("off")
        self.pad.light_up(lights)
    
    
    def plan(self, span):
        for column in self.columns:
            if hasattr(column, "plan"):
                column.plan(span)
        self._update_lights()
    
    def _handle_focus(self, event):
        """pushing button 0,8 (the topmost row launch button) causes the homepad
        to toggle 'focusing.' In order to go into a focused state, the user must
        push the button to focus while holding down the focus toggle."""
        
        if event.get_row() is 0 and event.get_column() is 8:
            if event.is_a_push():
                if self.active_column is None:
                    print "input context is now focus"
                    self.input_context = "focus"
                else:
                    self.active_column = None
            elif event.is_a_release():
                print "no input context"
                self.input_context = None
        
        #check to see if a button is being pressed while focus is being held down
        elif self.input_context is "focus":
            self.active_column = event.get_column()
            return True
        return False
    
    def read_input(self):
        for event in self.pad.read_input():
            event_handled = self._handle_focus(event)
            if not event_handled:
                if self.active_column == None:
                    self._send_column_event(event)
                else:
                    self._send_focused_event(event)

class BaseColumn(object):
    def __init__(self, clock):
        self.clock = clock
        self.column_lights = ["off" for x in range(0, 8)]
        self.focused_lights = ["off" for x in range(0, 64)]
    