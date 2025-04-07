import tkinter as tk
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.frontend.gui import Gui
from enum import IntEnum

# Mock classes to replace backend dependencies
class MockState(IntEnum):
    OFF = 0
    STANDBY = 1
    CALIBRATE = 2
    READY = 3
    ACTIVE = 4

class MockManager:
    def __init__(self):
        self.current_state = MockState.STANDBY
        self.gui = None  # Will be set after GUI is created
        
    def stop(self):
        print("Mock: Stopping system")
        self.current_state = MockState.OFF
        if self.gui:
            self.gui.set_state(self.current_state)
            self.gui.add_log("System stopped - Power OFF", 'info')
        
    def standby(self):
        print("Mock: Entering standby")
        self.current_state = MockState.STANDBY
        if self.gui:
            self.gui.set_state(self.current_state)
            self.gui.add_log("System entered STANDBY mode", 'info')
        
    def calibrate(self):
        print("Mock: Starting calibration")
        self.current_state = MockState.CALIBRATE
        if self.gui:
            self.gui.set_state(self.current_state)
            self.gui.add_log("Starting system calibration...", 'info')
        
    def ready(self):
        print("Mock: System ready")
        self.current_state = MockState.READY
        if self.gui:
            self.gui.set_state(self.current_state)
            self.gui.add_log("System is READY for operation", 'success')
        
    def active(self):
        print("Mock: System active")
        self.current_state = MockState.ACTIVE
        if self.gui:
            self.gui.set_state(self.current_state)
            self.gui.add_log("System is now ACTIVE and operational", 'success')

class MockGraph:
    def show(self):
        print("Mock: Showing visualization")
        if hasattr(self, 'gui'):
            self.gui.add_log("Opening 3D visualization...", 'info')

def main():
    root = tk.Tk()
    state_manager = MockManager()
    vis = MockGraph()
    gui = Gui(root, state_manager, vis)
    state_manager.gui = gui
    vis.gui = gui 
    
    # Set initial state and log
    gui.set_state(MockState.STANDBY)
    gui.add_log("System initialized in STANDBY mode", 'info')
    
    root.mainloop()

if __name__ == "__main__":
    main() 