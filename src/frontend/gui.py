import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np

from src.backend.state_management.state_manager import (
    Manager, MANUAL_TRANSITION_DICT, State
)
from src.frontend.visualisation import Graph


INSTRUCTIONS = ('PLACEHOLDER'
                'TEXT')


class Gui:

    root = None
    state_manager = None
    vis = None
    buttons = None
    log_list = None
    logs = None
    camera_frames = None
    trajectory_canvas = None
    
    # HSV thresholds for object detection
    low_H = 170
    low_S = 120
    low_V = 100
    high_H = 10
    high_S = 255
    high_V = 255
    max_value = 255
    max_value_H = 360//2

    def __init__(self, root, state_manager: Manager, vis: Graph):
        self.root = root
        self.root.title("Arm Control")
        self.root.geometry("1600x900")
        self.state_manager = state_manager
        self.vis = vis
        
        # Create main container
        main_container = tk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls and logs
        left_panel = tk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Control panel
        control_frame = tk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=5)
        
        # State buttons with consistent styling
        button_styles = {
            'OFF': {'bg': '#ff6b6b', 'activebackground': '#ff5252'},
            'STANDBY': {'bg': '#4ecdc4', 'activebackground': '#45b7af'},
            'CALIBRATE': {'bg': '#ffe66d', 'activebackground': '#ffd93d'},
            'READY': {'bg': '#95e1d3', 'activebackground': '#7fcdc0'},
            'ACTIVE': {'bg': '#a8e6cf', 'activebackground': '#8ed3b5'}
        }
        
        button_commands = {
            'OFF': state_manager.stop,
            'STANDBY': state_manager.standby,
            'CALIBRATE': state_manager.calibrate,
            'READY': state_manager.ready,
            'ACTIVE': state_manager.active
        }
        
        self.buttons = {}
        for i, (text, command) in enumerate(button_commands.items()):
            btn = tk.Button(control_frame, text=text, width=10, command=command,
                          **button_styles[text])
            btn.grid(row=0, column=i, padx=2)
            self.buttons[text] = btn
        
        # Log panel
        log_frame = tk.Frame(left_panel)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_list = tk.Listbox(log_frame, width=50, height=20,
                                  font=('Courier', 10))
        self.log_list.pack(fill=tk.BOTH, expand=True)
        
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
        
        self.camera_frames = []
        for i in range(2):
            frame = tk.Label(camera_frame, text="Camera not available", 
                           font=('Arial', 14), bg='#333333', fg='white')
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            self.camera_frames.append(frame)
        
        # Trajectory visualization
        trajectory_frame = tk.Frame(right_panel)
        trajectory_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.trajectory_canvas = tk.Canvas(trajectory_frame, bg='black')
        self.trajectory_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize cameras
        try:
            self.cap1 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            self.cap2 = cv2.VideoCapture(2, cv2.CAP_DSHOW)
            
            if not self.cap1.isOpened() or not self.cap2.isOpened():
                self.add_log("Warning: One or more cameras not available")
                self.cap1 = None
                self.cap2 = None
            else:
                self.add_log("Cameras initialized successfully")
        except Exception as e:
            self.add_log(f"Error initializing cameras: {str(e)}")
            self.cap1 = None
            self.cap2 = None
        
        # Start update loop
        self.update_cameras()
        self.update_trajectory()

    def create_threshold_controls(self, parent):
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
        return frame

    def update_cameras(self):
        if self.cap1 is not None and self.cap2 is not None:
            ret1, frame1 = self.cap1.read()
            ret2, frame2 = self.cap2.read()
            
            if ret1 and ret2:
                # Process frames
                frame1 = self.process_frame(frame1)
                frame2 = self.process_frame(frame2)
                
                # Convert to PhotoImage
                frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                
                img1 = Image.fromarray(frame1)
                img2 = Image.fromarray(frame2)
                
                # Resize to fit the display
                img1 = img1.resize((400, 300))
                img2 = img2.resize((400, 300))
                
                photo1 = ImageTk.PhotoImage(image=img1)
                photo2 = ImageTk.PhotoImage(image=img2)
                
                self.camera_frames[0].configure(image=photo1)
                self.camera_frames[1].configure(image=photo2)
                
                self.camera_frames[0].image = photo1
                self.camera_frames[1].image = photo2
        
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

    def set_state(self, state: State):
        """Update the active state and disable buttons for invalid transitions.
        """
        for text, btn in self.buttons.items():
            condition = MANUAL_TRANSITION_DICT[state] & (int('10000', 2) >> list(self.buttons.keys()).index(text))
            btn.config(state=tk.NORMAL if condition else tk.DISABLED)
            if condition:
                btn.config(borderwidth=4)
            else:
                btn.config(borderwidth=1)

    def add_log(self, log: str):
        """Add an entry to the log and highlight briefly.
        """
        self.log_list.insert(0, log)
        self.log_list.itemconfig(0, {'bg': 'yellow'})
        self.root.after(1000, self.clear_log_highlight)

    def clear_log_highlight(self):
        """Remove all highlights after 1 second.
        """
        for i in range(self.log_list.size()):
            self.log_list.itemconfig(i, {'bg': 'white'})

    def open_instructions(self):
        """Open window with instructions and close button.
        """
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Instructions")
        instructions_window.geometry("400x200")
        label = tk.Label(instructions_window, text=INSTRUCTIONS, font=("Arial", 10), wraplength=350, justify='center')
        label.pack(pady=10)
        close_button = tk.Button(instructions_window, text="Close", command=instructions_window.destroy)
        close_button.pack(pady=10)
