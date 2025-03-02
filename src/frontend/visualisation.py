from tkinter import Tk
from typing import Tuple
import numpy as np

from src.backend.external_management.connections import LEFT_CAM_OFFSET

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows: Enable DPI awareness
except AttributeError:
    pass  # Not running on Windows, ignore
from vispy import use
use('pyqt6')  # Explicitly set the backend before importing scene
from vispy import scene


class Graph:

    root = None
    canvas = None
    cam_scatter = None
    obj_scatter = None
    ray_lines = None

    def __init__(self, root: Tk):
        """Create static environment elements.
        """
        self.root = root
        self.cam_scatter = scene.visuals.Markers()
        cams = np.array([LEFT_CAM_OFFSET, (-LEFT_CAM_OFFSET[0], LEFT_CAM_OFFSET[1], LEFT_CAM_OFFSET[2])])
        self.cam_scatter.set_data(cams, face_color='black', size=5)
        self.obj_scatter = scene.visuals.Markers()

    def set_obj(self, location: Tuple[float, float, float]):
        """Set new location for object in visualisation.
        """
        self.obj_scatter.set_data(location, face_color='red', size=10)

    def set_cam_rays(self):
        """Set where cameras see object.
        """
        self.ray_lines = [
            scene.visuals.Line(pos=np.array([[0, 0, 0], [0, 0, 2]]), color='blue', width=2),
            scene.visuals.Line(pos=np.array([[0, 0, 0], [0, 0, 2]]), color='blue', width=2),
        ]

    def show(self):
        """Create and show visualisation.
        """
        # close if still open
        if self.canvas:
            self.canvas.close()
        # create canvas
        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
        self.canvas.bgcolor = 'white'
        # create view + details
        view = self.canvas.central_widget.add_view()
        view.camera = 'turntable'
        view.camera.center = (0, 0, 0)
        view.camera.scale_factor = 5
        scene.visuals.XYZAxis(parent=view.scene)
        # Add points + lines
        view.add(self.cam_scatter)
        view.add(self.obj_scatter)
        if self.ray_lines:
            view.add(self.ray_lines[0])
            view.add(self.ray_lines[1])
        # updates
        self.root.after(10, self.update)

    def update(self):
        """Ensure VisPy stays interactive
        """
        if self.canvas:
            self.canvas.app.process_events()
        self.root.after(10, self.update)

