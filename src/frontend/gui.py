import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from src.backend.state_management.state_manager import (
    Manager, MANUAL_TRANSITION_DICT, State
)
from src.frontend.visualisation import Graph


INSTRUCTIONS = ('Welcome to the Arm Control System!\n\n'
                '1. Start in STANDBY mode\n'
                '2. CALIBRATE the system\n'
                '3. Set to READY when prepared\n'
                '4. Switch to ACTIVE for operation\n'
                '5. Return to OFF to shutdown')


class Gui:
    root = None
    state_manager = None
    vis = None
    buttons = None
    log_list = None
    logs = None
    calibration_complete = False
    
    def __init__(self, root, state_manager: Manager, vis: Graph):
        self.root = root
        self.root.title("Arm Control")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Create custom fonts
        self.title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.button_font = tkfont.Font(family="Helvetica", size=12)
        self.log_font = tkfont.Font(family="Consolas", size=10)

        self.state_manager = state_manager
        self.vis = vis
        self.calibration_complete = False

        # Create main container with padding
        self.main_container = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create left and right frames
        self.left_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.right_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Setup control panel
        self.setup_control_panel()

        # Setup visualization panel
        self.setup_visualization_panel()

        # Setup log panel
        self.setup_log_panel()

    def setup_control_panel(self):
        """Setup the control panel with state buttons and controls"""
        control_frame = tk.LabelFrame(self.left_frame, text="System Controls", 
                                    font=self.title_font, bg='#f0f0f0', fg='#2c3e50',
                                    padx=10, pady=10)
        control_frame.pack(fill=tk.X, pady=(0, 20))

        # State buttons with modern styling
        button_commands = {
            'OFF': self.state_manager.stop,
            'STANDBY': self.state_manager.standby,
            'CALIBRATE': self.state_manager.calibrate,
            'READY': self.state_manager.ready,
            'ACTIVE': self.state_manager.active
        }

        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=10)

        self.buttons = []
        for i, (text, command) in enumerate(button_commands.items()):
            btn = tk.Button(button_frame, text=text,
                          font=self.button_font,
                          fg='#000000',
                          width=12, height=2,
                          command=command)
            btn.grid(row=0, column=i, padx=5, pady=5)
            self.buttons.append(btn)

        # Visualization button with modern styling
        vis_button = tk.Button(self.left_frame, text="System Visualization",
                             font=self.button_font,
                             fg='#000000',
                             command=self.vis.show)
        vis_button.pack(pady=10)

        # Instructions button with modern styling
        instructions_button = tk.Button(self.left_frame, text="Instructions",
                                      font=self.button_font,
                                      fg='#000000',
                                      command=self.open_instructions)
        instructions_button.pack(pady=10)

    def setup_visualization_panel(self):
        """Setup the visualization panel with camera feeds and trajectory visualization"""
        vis_frame = tk.LabelFrame(self.left_frame, text="Visualization", 
                                font=self.title_font, bg='#f0f0f0', fg='#2c3e50',
                                padx=10, pady=10)
        vis_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas with scrollbar for the entire visualization panel
        canvas = tk.Canvas(vis_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(vis_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame to hold both camera feeds
        camera_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
        camera_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Left camera feed
        left_camera_frame = tk.LabelFrame(camera_frame, text="Camera 1", 
                                        font=self.button_font, bg='#f0f0f0', fg='#2c3e50',
                                        padx=5, pady=5)
        left_camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.left_camera_canvas = tk.Canvas(left_camera_frame, bg='black', width=400, height=300)
        self.left_camera_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right camera feed
        right_camera_frame = tk.LabelFrame(camera_frame, text="Camera 2", 
                                         font=self.button_font, bg='#f0f0f0', fg='#2c3e50',
                                         padx=5, pady=5)
        right_camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.right_camera_canvas = tk.Canvas(right_camera_frame, bg='black', width=400, height=300)
        self.right_camera_canvas.pack(fill=tk.BOTH, expand=True)

        # Trajectory visualization
        trajectory_frame = tk.LabelFrame(scrollable_frame, text="Trajectory", 
                                       font=self.button_font, bg='#f0f0f0', fg='#2c3e50',
                                       padx=5, pady=5)
        trajectory_frame.pack(fill=tk.BOTH, expand=True)
        
        self.trajectory_canvas = tk.Canvas(trajectory_frame, bg='black', width=800, height=200)
        self.trajectory_canvas.pack(fill=tk.BOTH, expand=True)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel to scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _update_visualization(self):
        """Update the camera feeds and trajectory with placeholder content"""
        # Clear all canvases
        self.left_camera_canvas.delete("all")
        self.right_camera_canvas.delete("all")
        self.trajectory_canvas.delete("all")
        
        # Add placeholder text to both cameras
        self.left_camera_canvas.create_text(200, 150, 
                                          text="Camera 1 Feed\n(Placeholder)",
                                          fill='white', font=self.title_font,
                                          justify=tk.CENTER)
        
        self.right_camera_canvas.create_text(200, 150,
                                           text="Camera 2 Feed\n(Placeholder)",
                                           fill='white', font=self.title_font,
                                           justify=tk.CENTER)
        
        # Add state indicator to both feeds
        state_text = f"Current State: {self.state_manager.current_state.name}"
        self.left_camera_canvas.create_text(200, 250, text=state_text,
                                          fill='white', font=self.button_font)
        self.right_camera_canvas.create_text(200, 250, text=state_text,
                                           fill='white', font=self.button_font)

        # Add trajectory visualization
        # Draw grid
        for i in range(0, 800, 50):
            self.trajectory_canvas.create_line(i, 0, i, 200, fill='#333333', width=1)
        for i in range(0, 200, 20):
            self.trajectory_canvas.create_line(0, i, 800, i, fill='#333333', width=1)

        # Add axis labels
        self.trajectory_canvas.create_text(400, 190, text="X", fill='white', font=self.button_font)
        self.trajectory_canvas.create_text(790, 100, text="Y", fill='white', font=self.button_font)

    def setup_log_panel(self):
        """Setup the log panel with system messages"""
        log_frame = tk.LabelFrame(self.right_frame, text="System Log", 
                                font=self.title_font, bg='#f0f0f0', fg='#2c3e50',
                                padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Log text with modern styling
        self.log_list = tk.Text(log_frame, font=self.log_font,
                               bg='#ffffff', fg='#2c3e50',
                               relief=tk.FLAT, bd=1,
                               highlightthickness=1,
                               highlightcolor='#bdc3c7',
                               wrap=tk.WORD,
                               padx=10,
                               pady=5)
        self.log_list.pack(fill=tk.BOTH, expand=True)
        self.log_list.config(state=tk.DISABLED)

        # Add scrollbar to log text
        scrollbar = ttk.Scrollbar(self.log_list, orient=tk.VERTICAL,
                                command=self.log_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_list.config(yscrollcommand=scrollbar.set)

        # Configure tags for different message types
        self.log_list.tag_configure('error', foreground='#e74c3c')
        self.log_list.tag_configure('success', foreground='#2ecc71')
        self.log_list.tag_configure('info', foreground='#3498db')
        self.log_list.tag_configure('highlight', background='#fff3cd')
        self.log_list.tag_configure('timestamp', foreground='#95a5a6')

    def set_state(self, state: State):
        """Update the active state and disable buttons for invalid transitions."""
        for i, btn in enumerate(self.buttons):
            condition = MANUAL_TRANSITION_DICT[state] & (int('10000', 2) >> i)
            if condition:
                btn.config(state=tk.NORMAL)
            else:
                btn.config(state=tk.DISABLED)
                
            btn.config(borderwidth=4 if i == state else 1)
            btn.config(highlightbackground='#dd6' if i == state else '#fff')
        
        # Add log entry for state change with success tag
        self.add_log(f"System state changed to: {state.name}", 'success')
        
        # Handle calibration state
        if state == State.CALIBRATE:
            self.calibration_complete = False
            # Simulate calibration process
            self.root.after(2000, self._calibration_complete)
        elif state == State.READY and not self.calibration_complete:
            self.add_log("Calibration must be completed before setting to READY", 'error')
            return False
        elif state == State.READY:
            self.calibration_complete = False  # Reset for next time
            return True
            
        return True
        
    def _calibration_complete(self):
        """Handle calibration completion"""
        self.calibration_complete = True
        self.add_log("Calibration completed successfully", 'success')
        self.add_log("Please set system to READY state to continue", 'info')

    def add_log(self, log: str, tag='info'):
        """Add an entry to the log with appropriate styling"""
        self.log_list.config(state=tk.NORMAL)
        
        # Configure the text widget to maintain its size
        self.log_list.config(width=40, height=20)
        
        self.log_list.insert('1.0', log + '\n')
        self.log_list.tag_add('highlight', '1.0', '2.0')
        self.log_list.tag_add(tag, '1.0', '2.0')
        self.log_list.see('1.0')  # Auto-scroll to the latest entry
        self.log_list.config(state=tk.DISABLED)
        self.root.after(1000, self.clear_log_highlight)
        
        # Update visualization when state changes
        if "state changed to" in log:
            self._update_visualization()

    def clear_log_highlight(self):
        """Remove highlight after 1 second"""
        self.log_list.config(state=tk.NORMAL)
        self.log_list.tag_remove('highlight', '1.0', tk.END)
        self.log_list.config(state=tk.DISABLED)

    def open_instructions(self):
        """Open window with instructions and close button"""
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Instructions")
        instructions_window.geometry("400x200")
        label = tk.Label(instructions_window, text=INSTRUCTIONS, 
                        font=("Arial", 10), wraplength=350, justify='center')
        label.pack(pady=10)
        close_button = tk.Button(instructions_window, text="Close", 
                               command=instructions_window.destroy)
        close_button.pack(pady=10)
