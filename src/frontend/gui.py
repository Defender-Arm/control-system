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
        control_frame.pack(anchor='center', pady=5)
        
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
            btn = tk.Button(control_frame, text=text, width=10, command=command, font=("TkDefaultFont", 16),
                          **button_styles[text])
            btn.grid(row=0, column=i, padx=2)
            self.buttons[text] = btn
        
        # Log panel
        log_frame = tk.Frame(left_panel)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_list = tk.Listbox(log_frame, width=100, height=20,
                                  font=('Courier', 10))
        self.log_list.pack(fill=tk.BOTH, expand=True)
        
        # Right panel for other
        right_panel = tk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # vis frame
        control_frame = tk.Frame(right_panel)
        control_frame.pack(fill=tk.X, pady=5)

        # show graph button
        vis_button = tk.Button(control_frame, text="System Visualisation", command=vis.show)
        vis_button.pack(anchor='center', padx=5)

        # Trajectory visualization
        trajectory_frame = tk.Frame(right_panel)
        trajectory_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.trajectory_canvas = tk.Canvas(trajectory_frame, bg='black')
        self.trajectory_canvas.pack(fill=tk.BOTH, expand=True)

    def set_state(self, state: State):
        """Update the active state and disable buttons for invalid transitions.
        """
        for text, btn in self.buttons.items():
            condition = MANUAL_TRANSITION_DICT[state] & (int('10000', 2) >> list(self.buttons.keys()).index(text))
            btn.config(state=tk.NORMAL if condition else tk.DISABLED)
            btn.config(borderwidth=4 if state.name == text else 1)

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
