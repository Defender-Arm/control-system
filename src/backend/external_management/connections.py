from enum import IntEnum
from numpy import ndarray
from typing import Optional, Tuple


LEFT_CAM_INDEX = 0
RIGHT_CAM_INDEX = 1
LEFT_CAM_OFFSET = (0.0, 0.0, 0.0)  # TODO m from origin
LEFT_CAM_ANGLES = (0.0, 0.0, 0.0)  # TODO rad from origin
CAM_FOV = 0.0  # TODO rad
CAM_RESOLUTION = (0.0, 0.0)  # TODO pixel X * pixel Y

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
        raise NotImplementedError

    def verify_connection(self) -> bool:
        """Ensures all devices are connected.
        :return: If all devices connected"""
        raise NotImplementedError

    def take_photos(self) -> Tuple[Optional[ndarray], Optional[ndarray]]:
        """Gets snapshot from both cameras.
        :return: Arm's left camera image, then arm's right camera image. Image is ``None`` if camera cannot be reached.
        """
        raise NotImplementedError

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
