import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import cv2
import sys
import os
import time

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.gui import Gui
from backend.state_management.state_manager import Manager
from frontend.visualisation import Graph

class MockStateManager:
    """A mock state manager for testing the GUI without backend dependencies."""
    def __init__(self):
        self.current_state = 0  # OFF state
        
    def stop(self):
        print("Mock: Stopping")
        self.current_state = 0
        
    def standby(self):
        print("Mock: Going to standby")
        self.current_state = 1
        
    def calibrate(self):
        print("Mock: Calibrating")
        self.current_state = 2
        
    def ready(self):
        print("Mock: Ready")
        self.current_state = 3
        
    def active(self):
        print("Mock: Active")
        self.current_state = 4

class MockGraph:
    """A mock graph for testing the GUI without backend dependencies."""
    def show(self):
        print("Mock: Showing graph")

class MockCamera:
    """A mock camera that generates test patterns instead of real camera feeds."""
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self._frame_width = width
        self._frame_height = height
        
    def set(self, prop, value):
        """Mock implementation of cv2.VideoCapture.set"""
        if prop == cv2.CAP_PROP_FRAME_WIDTH:
            self._frame_width = value
        elif prop == cv2.CAP_PROP_FRAME_HEIGHT:
            self._frame_height = value
        return True
        
    def read(self):
        # Create a test pattern image
        frame = np.zeros((self._frame_height, self._frame_width, 3), dtype=np.uint8)
        
        # Add a grid
        for i in range(0, self._frame_width, 50):
            cv2.line(frame, (i, 0), (i, self._frame_height), (50, 50, 50), 1)
        for i in range(0, self._frame_height, 50):
            cv2.line(frame, (0, i), (self._frame_width, i), (50, 50, 50), 1)
            
        # Add a colored rectangle that moves around
        x = int((np.sin(cv2.getTickCount() / 1e9) + 1) * (self._frame_width - 100) / 2)
        y = int((np.cos(cv2.getTickCount() / 1e9) + 1) * (self._frame_height - 100) / 2)
        cv2.rectangle(frame, (x, y), (x + 100, y + 100), (0, 255, 0), 2)
        
        # Add a circle in the center
        cv2.circle(frame, (self._frame_width // 2, self._frame_height // 2), 30, (255, 0, 0), -1)
        
        return True, frame
        
    def isOpened(self):
        return True
        
    def release(self):
        pass

# Create a standalone GUI without any backend dependencies
class StandaloneGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Arm Control - Demo Mode")
        self.root.geometry("1600x900")
        
        # Create main container
        main_container = tk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls and logs
        left_panel = tk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Control panel
        control_frame = tk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Log panel
        log_frame = tk.Frame(left_panel)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_list = tk.Listbox(log_frame, width=50, height=20,
                                  font=('Courier', 10))
        self.log_list.pack(fill=tk.BOTH, expand=True)
        
        # Initialize logging
        self.add_log("Demo GUI started")
        self.add_log("Using mock cameras")
        self.add_log("State: OFF")
        
        # State buttons with consistent styling
        button_styles = {
            'OFF': {'bg': '#ff6b6b', 'activebackground': '#ff5252'},
            'STANDBY': {'bg': '#4ecdc4', 'activebackground': '#45b7af'},
            'CALIBRATE': {'bg': '#ffe66d', 'activebackground': '#ffd93d'},
            'READY': {'bg': '#95e1d3', 'activebackground': '#7fcdc0'},
            'ACTIVE': {'bg': '#a8e6cf', 'activebackground': '#8ed3b5'}
        }
        
        self.buttons = {}
        for i, (text, style) in enumerate(button_styles.items()):
            btn = tk.Button(control_frame, text=text, width=10, 
                          command=lambda t=text: self.button_click(t),
                          **style)
            btn.grid(row=0, column=i, padx=2)
            self.buttons[text] = btn
        
        # Right panel for camera feeds and trajectory
        right_panel = tk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Camera controls frame
        camera_controls = tk.Frame(right_panel)
        camera_controls.pack(fill=tk.X, pady=5)
        
        # HSV threshold controls
        threshold_frame = tk.LabelFrame(camera_controls, text="HSV Threshold Controls")
        threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create trackbars for HSV thresholds
        self.create_threshold_controls(threshold_frame)
        
        # Camera feeds
        camera_frame = tk.Frame(right_panel)
        camera_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create labels for camera views
        tk.Label(camera_frame, text="Original Frames", font=('Arial', 10)).grid(row=0, column=0, padx=5)
        tk.Label(camera_frame, text="Threshold Masks", font=('Arial', 10)).grid(row=0, column=1, padx=5)
        
        # Create labels for the camera views with fixed size
        self.camera_frames = []
        for i in range(2):
            frame = tk.Label(camera_frame, bg='black', width=400, height=300)
            frame.grid(row=1, column=i, padx=5, pady=5, sticky='nsew')
            self.camera_frames.append(frame)
            
        # Configure grid weights
        camera_frame.grid_columnconfigure(0, weight=1)
        camera_frame.grid_columnconfigure(1, weight=1)
        camera_frame.grid_rowconfigure(1, weight=1)
        
        # Trajectory visualization
        trajectory_frame = tk.Frame(right_panel)
        trajectory_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.trajectory_canvas = tk.Canvas(trajectory_frame, bg='black')
        self.trajectory_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize mock cameras
        self.cap1 = MockCamera()
        self.cap2 = MockCamera()
        
        # Set frame sizes to match mask2.py
        self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 20)
        self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 20)
        self.cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 20)
        self.cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 20)
        
        # Start update loop
        self.update_cameras()
        self.update_trajectory()
        
        # Current state
        self.current_state = "OFF"
    
    def create_threshold_controls(self, parent):
        # HSV thresholds
        self.low_H = 170
        self.low_S = 120
        self.low_V = 100
        self.high_H = 10
        self.high_S = 255
        self.high_V = 255
        self.max_value = 255
        self.max_value_H = 360//2
        
        # Low H threshold
        tk.Label(parent, text="Low H").grid(row=0, column=0, padx=5, pady=2)
        self.low_H_scale = tk.Scale(parent, from_=0, to=self.max_value_H,
                                  orient=tk.HORIZONTAL, command=self.on_low_H_thresh_trackbar)
        self.low_H_scale.set(self.low_H)
        self.low_H_scale.grid(row=0, column=1, padx=5, pady=2)
        
        # High H threshold
        tk.Label(parent, text="High H").grid(row=0, column=2, padx=5, pady=2)
        self.high_H_scale = tk.Scale(parent, from_=0, to=self.max_value_H,
                                   orient=tk.HORIZONTAL, command=self.on_high_H_thresh_trackbar)
        self.high_H_scale.set(self.high_H)
        self.high_H_scale.grid(row=0, column=3, padx=5, pady=2)
        
        # Low S threshold
        tk.Label(parent, text="Low S").grid(row=1, column=0, padx=5, pady=2)
        self.low_S_scale = tk.Scale(parent, from_=0, to=self.max_value,
                                  orient=tk.HORIZONTAL, command=self.on_low_S_thresh_trackbar)
        self.low_S_scale.set(self.low_S)
        self.low_S_scale.grid(row=1, column=1, padx=5, pady=2)
        
        # High S threshold
        tk.Label(parent, text="High S").grid(row=1, column=2, padx=5, pady=2)
        self.high_S_scale = tk.Scale(parent, from_=0, to=self.max_value,
                                   orient=tk.HORIZONTAL, command=self.on_high_S_thresh_trackbar)
        self.high_S_scale.set(self.high_S)
        self.high_S_scale.grid(row=1, column=3, padx=5, pady=2)
        
        # Low V threshold
        tk.Label(parent, text="Low V").grid(row=2, column=0, padx=5, pady=2)
        self.low_V_scale = tk.Scale(parent, from_=0, to=self.max_value,
                                  orient=tk.HORIZONTAL, command=self.on_low_V_thresh_trackbar)
        self.low_V_scale.set(self.low_V)
        self.low_V_scale.grid(row=2, column=1, padx=5, pady=2)
        
        # High V threshold
        tk.Label(parent, text="High V").grid(row=2, column=2, padx=5, pady=2)
        self.high_V_scale = tk.Scale(parent, from_=0, to=self.max_value,
                                   orient=tk.HORIZONTAL, command=self.on_high_V_thresh_trackbar)
        self.high_V_scale.set(self.high_V)
        self.high_V_scale.grid(row=2, column=3, padx=5, pady=2)
    
    def on_low_H_thresh_trackbar(self, val):
        self.low_H = int(val)
        self.low_H_scale.set(self.low_H)
    
    def on_high_H_thresh_trackbar(self, val):
        self.high_H = int(val)
        self.high_H_scale.set(self.high_H)
    
    def on_low_S_thresh_trackbar(self, val):
        self.low_S = int(val)
        self.low_S = min(self.high_S-1, self.low_S)
        self.low_S_scale.set(self.low_S)
    
    def on_high_S_thresh_trackbar(self, val):
        self.high_S = int(val)
        self.high_S = max(self.high_S, self.low_S+1)
        self.high_S_scale.set(self.high_S)
    
    def on_low_V_thresh_trackbar(self, val):
        self.low_V = int(val)
        self.low_V = min(self.high_V-1, self.low_V)
        self.low_V_scale.set(self.low_V)
    
    def on_high_V_thresh_trackbar(self, val):
        self.high_V = int(val)
        self.high_V = max(self.high_V, self.low_V+1)
        self.high_V_scale.set(self.high_V)
    
    def process_frame(self, frame):
        frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame_threshold_1 = cv2.inRange(frame_HSV, (self.low_H, self.low_S, self.low_V), 
                                      (180, self.high_S, self.high_V))
        frame_threshold_2 = cv2.inRange(frame_HSV, (0, self.low_S, self.low_V), 
                                      (self.high_H, self.high_S, self.high_V))
        frame_threshold = frame_threshold_1 + frame_threshold_2

        kernel = np.ones((5, 5), np.uint8)
        frame_threshold = cv2.morphologyEx(frame_threshold, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(frame_threshold, cv2.RETR_EXTERNAL, 
                                     cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            rect = cv2.minAreaRect(largest_contour)
            box = cv2.boxPoints(rect).astype(int)
            center = (int(rect[0][0]), int(rect[0][1]))
            cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
            cv2.circle(frame, center, 5, (255, 0, 0), -1)
        return frame, frame_threshold
    
    def update_cameras(self):
        """Update the camera feeds with new frames."""
        if self.cap1 is not None and self.cap2 is not None:
            ret1, frame1 = self.cap1.read()
            ret2, frame2 = self.cap2.read()
            
            if ret1 and ret2:
                # Process frames
                frame1, mask1 = self.process_frame(frame1)
                frame2, mask2 = self.process_frame(frame2)
                
                # Convert frames to RGB
                frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                
                # Convert masks to RGB (repeat the single channel 3 times)
                mask1 = cv2.cvtColor(mask1, cv2.COLOR_GRAY2RGB)
                mask2 = cv2.cvtColor(mask2, cv2.COLOR_GRAY2RGB)
                
                # Create combined images
                combined_frame = np.hstack((frame1, frame2))
                combined_mask = np.hstack((mask1, mask2))
                
                # Convert to PIL Image
                img_frame = Image.fromarray(combined_frame)
                img_mask = Image.fromarray(combined_mask)
                
                # Resize to fit the display
                img_frame = img_frame.resize((400, 300))
                img_mask = img_mask.resize((400, 300))
                
                # Convert to PhotoImage
                photo_frame = ImageTk.PhotoImage(image=img_frame)
                photo_mask = ImageTk.PhotoImage(image=img_mask)
                
                # Update labels with new images
                self.camera_frames[0].configure(image=photo_frame)
                self.camera_frames[1].configure(image=photo_mask)
                
                # Keep references to prevent garbage collection
                self.camera_frames[0].image = photo_frame
                self.camera_frames[1].image = photo_mask
        
        self.root.after(30, self.update_cameras)
    
    def update_trajectory(self):
        self.trajectory_canvas.delete("all")
        
        # Draw grid
        width = self.trajectory_canvas.winfo_width()
        height = self.trajectory_canvas.winfo_height()
        
        # Draw horizontal lines
        for i in range(0, height, 50):
            self.trajectory_canvas.create_line(0, i, width, i, fill='#333333')
        
        # Draw vertical lines
        for i in range(0, width, 50):
            self.trajectory_canvas.create_line(i, 0, i, height, fill='#333333')
        
        # Draw robot arm representation
        center_x = width // 2
        center_y = height // 2
        
        # Base
        self.trajectory_canvas.create_oval(center_x-20, center_y-20, 
                                         center_x+20, center_y+20, 
                                         fill='#666666')
        
        # Arm segments (example)
        self.trajectory_canvas.create_line(center_x, center_y, 
                                         center_x+100, center_y-100, 
                                         fill='#4ecdc4', width=3)
        
        # Update every 100ms
        self.root.after(100, self.update_trajectory)
    
    def add_log(self, log: str):
        """Add an entry to the log and highlight briefly."""
        self.log_list.insert(0, log)
        self.log_list.itemconfig(0, {'bg': 'yellow'})
        self.root.after(1000, self.clear_log_highlight)
    
    def clear_log_highlight(self):
        """Remove all highlights after 1 second."""
        for i in range(self.log_list.size()):
            self.log_list.itemconfig(i, {'bg': 'white'})
    
    def button_click(self, state):
        """Handle button clicks and update the state."""
        self.current_state = state
        self.add_log(f"State changed to: {state}")
        
        # Update button states based on the current state
        # This is a simplified version of the state transition logic
        if state == "OFF":
            for text, btn in self.buttons.items():
                btn.config(state=tk.NORMAL if text == "STANDBY" else tk.DISABLED)
                btn.config(borderwidth=4 if text == state else 1)
        elif state == "STANDBY":
            for text, btn in self.buttons.items():
                btn.config(state=tk.NORMAL if text in ["OFF", "CALIBRATE"] else tk.DISABLED)
                btn.config(borderwidth=4 if text == state else 1)
        elif state == "CALIBRATE":
            for text, btn in self.buttons.items():
                btn.config(state=tk.NORMAL if text in ["OFF", "READY"] else tk.DISABLED)
                btn.config(borderwidth=4 if text == state else 1)
        elif state == "READY":
            for text, btn in self.buttons.items():
                btn.config(state=tk.NORMAL if text in ["OFF", "ACTIVE"] else tk.DISABLED)
                btn.config(borderwidth=4 if text == state else 1)
        elif state == "ACTIVE":
            for text, btn in self.buttons.items():
                btn.config(state=tk.NORMAL if text in ["OFF", "READY"] else tk.DISABLED)
                btn.config(borderwidth=4 if text == state else 1)

def main():
    # Create the main window
    root = tk.Tk()
    
    # Create the standalone GUI
    gui = StandaloneGui(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 