from typing import Tuple
from math import cos, atan, pi


D_TO_R = 2*pi/360
R_TO_D = 360/2*pi


def arm_angles_to_position(base: float, elbow: float, wrist: float) -> Tuple[float, float, float]:
    """Converts angles of arm to a position in space relative to the base. "Forward kinematics."
    :return: Distances in metres to right, then to front, then to above base joint
    """
    raise NotImplementedError


def pos_to_arm_angles(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Converts point to block to arm angles required to block it. "Reverse Kinematics."
    :return: Angles in radians for each arm joint
    """
    base = atan(x/y)
    elbow = atan(z/(y / cos(base)))
    wrist = base + pi/2
    return base, elbow, wrist
