import cv2
from enum import IntEnum
from numpy import ndarray
from typing import Optional, Tuple

from src.backend.error.standby_transition import StandbyTransition


LEFT_CAM_INDEX = 1
RIGHT_CAM_INDEX = 2
LEFT_CAM_OFFSET = (0.2, 0.0, 0.0)  # TODO m from origin
LEFT_CAM_ANGLES = (0.0, 0.0, 0.0)  # TODO rad from origin
CAM_FOV = 110.0  # TODO rad
CAM_RESOLUTION = (1920, 1080)  # TODO pixel X * pixel Y

ARM_BASE_LENGTH = 0.268  # metres
ARM_FORE_LENGTH = 0.1665
ARM_COLLISION_LENGTH = 0.175
ARM_SWORD_LENGTH = ARM_COLLISION_LENGTH * 2


class Joint(IntEnum):
    BASE = 0
    ELBOW = 1
    WRIST = 2


class Ext:

    def __init__(self):
        """Creates and stores all connections to external devices.
        """
        self._right_cam = None
        self._left_cam = None
        self.connect_cameras()

    def connect_cameras(self):
        """Opens connection to cameras.
        """
        self._left_cam = cv2.VideoCapture(LEFT_CAM_INDEX)
        self._right_cam = cv2.VideoCapture(RIGHT_CAM_INDEX)

    def disconnect_cameras(self):
        """Releases captures.
        """
        if self._left_cam:
            self._left_cam.release()
        if self._right_cam:
            self._right_cam.release()

    def verify_connection(self):
        """Ensures all devices are connected.
        :raise StandbyTransition: At least one device is not reachable/connected.
        """
        if not self._left_cam or not self._left_cam.isOpened():
            raise StandbyTransition(f'Left camera {LEFT_CAM_INDEX} is not open')
        if not self._right_cam or not self._right_cam.isOpened():
            raise StandbyTransition(f'Right camera {RIGHT_CAM_INDEX} is not open')

    def take_photos(self) -> Tuple[ndarray, ndarray]:
        """Gets snapshot from both cameras.
        :return: Arm's left camera image, then arm's right camera image. Image is ``None`` if camera cannot be reached.
        """
        ret, frame_l = self._left_cam.read()
        if not ret:
            raise StandbyTransition(f'Left camera {LEFT_CAM_INDEX} failed to read')
        ret, frame_r = self._right_cam.read()
        if not ret:
            raise StandbyTransition(f'Right camera {RIGHT_CAM_INDEX} failed to read')
        return frame_l, frame_r

    def arm_angles(self) -> Tuple[float, float, float]:
        """Gets angles of all arm joints, from base to end effector.
        :return: Base angle, then "elbow" angle, then "wrist" angle. Angle is ``None`` if sensor cannot be reached.
        """
        raise NotImplementedError

    def move_joint(self) -> None:
        """Changes angle of specified joint by specified value.
        """
        raise NotImplementedError


def arm_angles_to_position(base: float, elbow: float, wrist: float) -> Tuple[float, float, float]:
    """Converts angles of arm to a position in space relative to the base.
    :return: Distances in metres to right, then to front, then to above base joint
    """
    raise NotImplementedError
