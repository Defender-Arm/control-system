import tkinter as tk
import cv2
from numpy import ndarray

from src.backend.state_management.state_manager import (
    Manager, MANUAL_TRANSITION_DICT, State
)
from src.frontend.visualisation import Graph


CAM_WINDOW_NAME = 'Camera Feed'
INSTRUCTIONS = ('PLACEHOLDER'
                'TEXT')


class Gui:

    root = None
    state_manager = None
    vis = None
    buttons = None
    log_list = None
    logs = None
    show_cam_view = None

    def __init__(self, root, state_manager: Manager, vis: Graph):
        self.root = root
        self.root.title("Arm Control")
        self.root.geometry("1200x400")
        self.state_manager = state_manager
        self.vis = vis
        self.show_cam_view = False
        # left column; control
        control_frame = tk.Frame(root)
        control_frame.grid(row=0, column=0, padx=10, pady=10)
        # state buttons
        btn_off = tk.Button(control_frame, text='OFF', width=10, command=state_manager.stop)
        btn_off.grid(row=0, column=0, padx=2)
        btn_sby = tk.Button(control_frame, text='STANDBY', width=10, command=state_manager.standby)
        btn_sby.grid(row=0, column=1, padx=2)
        btn_cal = tk.Button(control_frame, text='CALIBRATE', width=10, command=state_manager.calibrate)
        btn_cal.grid(row=0, column=2, padx=2)
        btn_rdy = tk.Button(control_frame, text='READY', width=10, command=state_manager.ready)
        btn_rdy.grid(row=0, column=3, padx=2)
        btn_act = tk.Button(control_frame, text='ACTIVE', width=10, command=state_manager.active)
        btn_act.grid(row=0, column=4, padx=2)
        self.buttons = (btn_off, btn_sby, btn_cal, btn_rdy, btn_act)
        # show graph button / show cams button
        vis_frame = tk.Frame(root)
        vis_frame.grid(row=1, column=0, padx=10, pady=10)
        vis_button = tk.Button(vis_frame, text="System Visualisation", command=vis.show)
        vis_button.grid(row=0, column=0, padx=10)
        cam_button = tk.Button(vis_frame, text="Cam View", command=self.toggle_cam_view)
        cam_button.grid(row=0, column=1, padx=10)
        # show instructions button
        instructions_button = tk.Button(root, text="Instructions", command=self.open_instructions)
        instructions_button.grid(row=2, column=0, pady=10)
        # right column; logs
        log_frame = tk.Frame(root)
        log_frame.grid(row=0, column=1, padx=10, pady=10, rowspan=3)
        self.log_list = tk.Listbox(log_frame, width=80, height=15)
        self.log_list.pack()

    def set_state(self, state: State):
        """Update the active state and disable buttons for invalid transitions.
        """
        for i, btn in enumerate(self.buttons):
            condition = MANUAL_TRANSITION_DICT[state] & (int('10000', 2) >> i)
            btn.config(state=tk.NORMAL if condition else tk.DISABLED, background='#fff' if condition else '#ddd')
            btn.config(borderwidth=4 if i == state else 1, highlightbackground='#dd6' if i == state else '#fff')

    def add_log(self, log: str):
        """Add an entry to the log and highlight briefly.
        """
        self.log_list.insert(0, log)
        self.log_list.itemconfig(0, {'bg': 'yellow'})
        self.root.after(1000, self.clear_log_highlight)

    def toggle_cam_view(self):
        """Toggle showing view of cameras in a window to the user.
        """
        def safe_close_cam_window():
            try:
                cv2.destroyWindow(CAM_WINDOW_NAME)
            except cv2.error:
                pass  # Ignore if already closed or not created
        self.show_cam_view = not self.show_cam_view
        # Defer window close to avoid freezing
        if not self.show_cam_view:
            self.root.after(100, safe_close_cam_window)

    def cam_feed(self, frame: ndarray):
        """Sets image to show for camera visualisation.
        """
        if self.show_cam_view:
            cv2.imshow(CAM_WINDOW_NAME, frame)
            cv2.waitKey(1)

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
