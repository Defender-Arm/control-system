import tkinter as tk
from typing import List

from src.backend.state_management.state_manager import (
    Manager, MANUAL_TRANSITION_DICT, State
)
from src.frontend.visualisation import Graph


INSTRUCTIONS = ('Hello'
                'its me and its ho it work yes mmmmm one two thrre four five six ecsven eight '
                'nine ten eleven twelve thirteen frtoureen fifcteen')


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
        self.state_manager = state_manager
        self.vis = vis
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
        # show graph button
        vis_button = tk.Button(root, text="System Visualisation", command=vis.show)
        vis_button.grid(row=1, column=0, pady=10)
        # show instructions button
        instructions_button = tk.Button(root, text="Instructions", command=self.open_instructions)
        instructions_button.grid(row=2, column=0, pady=10)
        # right column; logs
        log_frame = tk.Frame(root)
        log_frame.grid(row=0, column=1, padx=10, pady=10, rowspan=2)
        self.log_list = tk.Listbox(log_frame, width=40, height=15)
        self.log_list.pack()

    def set_state(self, state: State):
        """Update the active state and disable buttons for invalid transitions.
        """
        if state is State.OFF:
            self.root.destroy()
        for i, btn in enumerate(self.buttons):
            condition = MANUAL_TRANSITION_DICT[state] & (int('10000', 2) >> i)
            btn.config(state=tk.NORMAL if condition else tk.DISABLED, background='#fff' if condition else '#ddd')
            btn.config(borderwidth=4 if i == state else 1, highlightbackground='#dd6' if i == state else '#fff')

    def set_logs(self, logs: List[str]):
        """Add an entry to the log and highlight briefly"""
        if len(logs) == 0:
            return
        self.log_list.delete(0, tk.END)
        for line in logs:
            self.log_list.insert(tk.END, line)
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
        instructions_window.geometry("400x200")  # Set window size
        label = tk.Label(instructions_window, text=INSTRUCTIONS, font=("Arial", 10), wraplength=350, justify='center')
        label.pack(pady=10)
        close_button = tk.Button(instructions_window, text="Close", command=instructions_window.destroy)
        close_button.pack(pady=10)
