from threading import Thread
import tkinter as tk

from src.backend.arm_control.op_loop import operation_loop
from src.backend.external_management.connections import Ext, is_arduino_connected
from src.backend.state_management.state_manager import Manager
from src.frontend.visualisation import Graph
from src.frontend.gui import Gui

IGNORE_MOTORS = False
IGNORE_CAMERAS = False

if __name__ == '__main__':
    # pre-check
    if IGNORE_CAMERAS:
        print('!!!!! IGNORING CAMERAS')
    if IGNORE_MOTORS:
        print('!!!!! IGNORING SERIAL CONNECTION')
    elif not is_arduino_connected():
        print('Please connect Arduino')
        exit(1)
    # create instances
    state_manager = Manager()
    connection_manager = Ext(ignore_motors=IGNORE_MOTORS, ignore_cameras=IGNORE_CAMERAS)
    root = tk.Tk()
    vis = Graph(root)
    gui = Gui(root, state_manager, vis)
    gui.set_state(state_manager.get_state())
    # start processing thread
    operation_thread = Thread(target=operation_loop, args=(state_manager, connection_manager, gui, vis))
    operation_thread.start()
    # start GUI thread
    root.mainloop()
    # trigger operation_thread cleanup if GUI closes first
    state_manager.stop()
    operation_thread.join()
    print('FINISHED')
