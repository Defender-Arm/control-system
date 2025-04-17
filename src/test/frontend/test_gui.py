import tkinter as tk
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
        self.calibration_complete = False
        
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
            
            # Simulate calibration process
            self.gui.root.after(2000, self._calibration_complete)
    
    def _calibration_complete(self):
        """Simulate calibration completion"""
        if self.gui:
            self.gui.add_log("Calibration completed successfully", 'success')
            self.gui.add_log("Please set system to READY state to continue", 'info')
            self.calibration_complete = True
        
    def ready(self):
        if not self.calibration_complete and self.current_state == MockState.CALIBRATE:
            if self.gui:
                self.gui.add_log("Calibration must be completed before setting to READY", 'error')
            return
            
        print("Mock: System ready")
        self.current_state = MockState.READY
        if self.gui:
            self.gui.set_state(self.current_state)
            self.gui.add_log("System is READY for operation", 'success')
            self.calibration_complete = False  # Reset for next time
        
    def active(self):
        print("Mock: System active")
        self.current_state = MockState.ACTIVE
        if self.gui:
            self.gui.set_state(self.current_state)
            self.gui.add_log("System is now ACTIVE and operational", 'success')

class MockGraph:
    def __init__(self):
        self.gui = None
        self.left_camera_canvas = None
        self.right_camera_canvas = None
        self.trajectory_canvas = None
        self.vis_canvas = None  # Add reference to the main visualization canvas

    def show(self):
        print("Mock: Showing visualization")
        if hasattr(self, 'gui'):
            self.gui.add_log("Opening visualization...", 'info')
            self._update_visualization()
            # Ensure the trajectory is visible by scrolling to the bottom
            if self.vis_canvas:
                self.vis_canvas.yview_moveto(1.0)  # Scroll to bottom

    def _update_visualization(self):
        """Update the camera feeds and trajectory with demo content"""
        if not self.gui:
            return

        # Clear all canvases
        self.gui.left_camera_canvas.delete("all")
        self.gui.right_camera_canvas.delete("all")
        self.gui.trajectory_canvas.delete("all")
        
        # Add demo content to both cameras
        self.gui.left_camera_canvas.create_text(200, 150, 
                                               text="Camera 1 Feed\n(Demo)",
                                               fill='white', font=self.gui.title_font,
                                               justify=tk.CENTER)
        
        self.gui.right_camera_canvas.create_text(200, 150,
                                                text="Camera 2 Feed\n(Demo)",
                                                fill='white', font=self.gui.title_font,
                                                justify=tk.CENTER)
        
        # Add state indicator to both feeds
        state_text = f"Current State: {self.gui.state_manager.current_state.name}"
        self.gui.left_camera_canvas.create_text(200, 250, text=state_text,
                                               fill='white', font=self.gui.button_font)
        self.gui.right_camera_canvas.create_text(200, 250, text=state_text,
                                                fill='white', font=self.gui.button_font)

        # Add trajectory visualization
        # Draw grid
        for i in range(0, 800, 50):
            self.gui.trajectory_canvas.create_line(i, 0, i, 200, fill='#333333', width=1)
        for i in range(0, 200, 20):
            self.gui.trajectory_canvas.create_line(0, i, 800, i, fill='#333333', width=1)

        # Add axis labels
        self.gui.trajectory_canvas.create_text(400, 190, text="X", fill='white', font=self.gui.button_font)
        self.gui.trajectory_canvas.create_text(790, 100, text="Y", fill='white', font=self.gui.button_font)

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