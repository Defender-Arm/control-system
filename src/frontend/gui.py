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
        """Setup the visualization panel"""
        vis_frame = tk.LabelFrame(self.left_frame, text="Visualization", 
                                font=self.title_font, bg='#f0f0f0', fg='#2c3e50',
                                padx=10, pady=10)
        vis_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for visualization
        canvas = tk.Canvas(vis_frame, bg='black', width=500, height=400)
        canvas.pack(fill=tk.BOTH, expand=True, pady=10)

        # Add some demo content to the canvas
        canvas.create_text(250, 200, text="3D Visualization\nDemo", 
                         fill='white', font=self.title_font)

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

    def add_log(self, log: str, tag='info'):
        """Add an entry to the log with appropriate styling"""
        self.log_list.config(state=tk.NORMAL)
        self.log_list.insert('1.0', log + '\n')
        self.log_list.tag_add('highlight', '1.0', '2.0')
        self.log_list.tag_add(tag, '1.0', '2.0')
        self.log_list.see('1.0')  # Auto-scroll to the latest entry
        self.log_list.config(state=tk.DISABLED)
        self.root.after(1000, self.clear_log_highlight)

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
