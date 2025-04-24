import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np

from src.backend.state_management.state_manager import (
    Manager, MANUAL_TRANSITION_DICT, State
)
from src.frontend.visualisation import Graph
from src.backend.sensor_fusion.tracking import find_in_image


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
        
        # Camera feeds
        camera_frame = tk.Frame(right_panel)
        camera_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create frames for camera views
        self.camera_frames = []
        for i in range(2):
            camera_container = tk.Frame(camera_frame)
            camera_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            # Camera view
            frame = tk.Label(camera_container, text="Camera not available", 
                           font=('Arial', 14), bg='#333333', fg='white')
            frame.pack(fill=tk.BOTH, expand=True)
            
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
            
            # Set lower resolution for faster processing
            self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
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

    def update_cameras(self):
        if self.cap1 is not None and self.cap2 is not None:
            ret1, frame1 = self.cap1.read()
            ret2, frame2 = self.cap2.read()
            
            if ret1 and ret2:
                try:
                    # Process frames using find_in_image
                    center1, angle1 = find_in_image(frame1)
                    center2, angle2 = find_in_image(frame2)
                    
                    # Draw the results on the frames
                    if center1 is not None:
                        cv2.circle(frame1, center1, 5, (255, 0, 0), -1)
                    if center2 is not None:
                        cv2.circle(frame2, center2, 5, (255, 0, 0), -1)
                    
                    # Convert to PhotoImage for display
                    frame1_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                    frame2_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                    
                    img1 = Image.fromarray(frame1_rgb)
                    img2 = Image.fromarray(frame2_rgb)
                    
                    # Resize to fit the display
                    img1 = img1.resize((400, 300))
                    img2 = img2.resize((400, 300))
                    
                    photo1 = ImageTk.PhotoImage(image=img1)
                    photo2 = ImageTk.PhotoImage(image=img2)
                    
                    # Update camera views
                    self.camera_frames[0].configure(image=photo1)
                    self.camera_frames[1].configure(image=photo2)
                    
                    self.camera_frames[0].image = photo1
                    self.camera_frames[1].image = photo2
                    
                except Exception as e:
                    self.add_log(f"Error processing frames: {str(e)}")
        
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
