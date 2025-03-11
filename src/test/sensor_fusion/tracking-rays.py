import tkinter as tk
from time import sleep
from threading import Thread
from random import random

from src.frontend.visualisation import Graph
from src.backend.sensor_fusion.tracking import (
    find_in_image, create_ray, locate_object, store_location
)
from src.backend.external_management.connections import CAM_RESOLUTION


def r():
    #return 1
    return random()/2


def dummy(gui):
    print('starting mock track...')
    dir = 1
    offset = -10
    while gui.running:
        ray_l = create_ray(2*CAM_RESOLUTION[0]/3 + offset, CAM_RESOLUTION[1]/2 + r() * 4)
        ray_r = create_ray(CAM_RESOLUTION[0]/3 + offset, CAM_RESOLUTION[1]/2 + r() * 4)
        vis.set_cam_rays(ray_l, ray_r)
        location, q1, q2 = locate_object(ray_l, ray_r)
        vis.set_obj((location,q1,q2))
        sleep(0.05)
        offset += dir * r() * 2
        if offset <= -10:
            dir = 1
            print('pong')
        elif offset >= 10:
            dir = -1
            print('ping')
    print('mock track ended')


class TesterGui:
    def __init__(self, root, vis):
        self.root = root
        self.vis = vis
        self.running = True

        control_frame = tk.Frame(root)
        control_frame.grid(row=0, column=0, padx=10, pady=10)
        # show graph button
        vis_button = tk.Button(root, text="System Visualisation", command=vis.show)
        vis_button.grid(row=1, column=0, pady=10)
        # show instructions button
        instructions_button = tk.Button(root, text="END", command=self.endit)
        instructions_button.grid(row=2, column=0, pady=10)

    def endit(self):
        self.running = False
        self.root.destroy()


root = tk.Tk()
flag = [True]
vis = Graph(root)
gui = TesterGui(root, vis)

operation_thread = Thread(target=dummy, args=(gui,))
operation_thread.start()

root.mainloop()




