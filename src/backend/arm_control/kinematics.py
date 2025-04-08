from typing import Tuple
from math import cos, sin, atan, pi


D_TO_R = 2*pi/360
R_TO_D = 360/(2*pi)
RESEND_DEG_THRESH = 15
MAGIC_NUMBER = 1.5


def arm_angles_to_position(base: float, elbow: float, wrist: float) -> Tuple[float, float, float]:
    """Converts angles of arm to a position in space relative to the base. "Forward kinematics."
    :return: Distances in metres to right, then to front, then to above base joint
    """
    raise NotImplementedError


def pos_to_arm_angles(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Converts point to block to arm angles required to block it. "Reverse Kinematics."
    :return: Angles in radians for each arm joint
    """

    base = atan(x/y) * MAGIC_NUMBER
    base_offset = base + (cos(base) * pi/12)
    elbow = atan(z/(y / cos(base))) * MAGIC_NUMBER + (sin(base) * pi/12)
    wrist = -base * MAGIC_NUMBER + pi/2
    return base_offset, elbow, wrist
