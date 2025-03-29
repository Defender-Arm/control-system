from src.backend.external_management.connections import (
    LEFT_CAM_OFFSET,
    LEFT_CAM_ANGLES,
    CAM_FOV
)
from src.backend.error.standby_transition import StandbyTransition

import cv2
from math import cos, sin, dist
import numpy
from time import monotonic
from typing import List, Optional, Tuple


LOWER_RED_1 = numpy.array([0, 120, 70])
UPPER_RED_1 = numpy.array([10, 255, 255])
LOWER_RED_2 = numpy.array([170, 120, 70])
UPPER_RED_2 = numpy.array([180, 255, 255])


_history = []


def find_in_image(image: numpy.ndarray) -> Optional[Tuple[Tuple[int, int], float]]:
    """Finds the pixel coordinates of the centre of the object in the image.
    :raise StandbyTransition: Unable to locate an object in the image similar enough to the target colour
    :return: Pixel location, (x, y) from top left, angle from upwards; None if object could not be found
    """
    # convert to HSV for processing
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Create masks for red color
    mask1 = cv2.inRange(hsv, LOWER_RED_1, UPPER_RED_1)
    mask2 = cv2.inRange(hsv, LOWER_RED_2, UPPER_RED_2)
    mask = mask1 + mask2
    # Apply morphological operations to remove noise
    kernel = numpy.ones((5, 5), numpy.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Find the largest contour (assuming it's the stick)
        largest_contour = max(contours, key=cv2.contourArea)
        # Fit a rotated rectangle
        rect = cv2.minAreaRect(largest_contour)
        # Extract center and orientation
        center = (int(rect[0][0]), int(rect[0][1]))  # x, y
        angle = rect[2]  # Rotation angle
        return center, angle
    else:
        raise StandbyTransition('Unable to determine possible location of sword')


def create_ray(pixel_x: int, pixel_y: int, res: Tuple) -> Tuple[float, float]:
    """Calculates angles for line in real space which passes from the center of
    the camera through the object in the image.
    :return: Angles in radians from camera along x-axis (right), then y-axis (up)
    """
    angle_x = (pixel_x / res[0]) * CAM_FOV - (CAM_FOV / 2)
    vertical_fov = (res[1] / res[0]) * CAM_FOV
    angle_y = -((pixel_y / res[1]) * vertical_fov - (vertical_fov / 2))
    return angle_x, angle_y


def angles_to_vector(angle_x: float, angle_y: float) -> Tuple[float, float, float]:
    """Converts xy and yz angles to a vector.
    :return: Unit vector
    """
    x = sin(angle_x) * cos(angle_y)
    y = cos(angle_x) * cos(angle_y)
    z = sin(angle_y)
    return x, y, z


def locate_object(
        left_ray_angles: Tuple[float, float],
        right_ray_angles: Tuple[float, float]
) -> numpy.typing.NDArray[numpy.float64]:
    """Finds where two rays intersect or are the closest to intercepting.
    :raise StandbyTransition: Rays do not intersect and shortest distance between them is greater than 0.1 metre
    :return: Metres from base joint; x-axis, then y-axis, then z-axis
    """
    # parametric vectors r(t) = p + t*d, CAM_OFFSET = p, left = r1, right = r2 (see Cramer's rule)
    d1 = numpy.array(angles_to_vector(left_ray_angles[0] + LEFT_CAM_ANGLES[0], left_ray_angles[1] + LEFT_CAM_ANGLES[1]))
    d2 = numpy.array(angles_to_vector(right_ray_angles[0] - LEFT_CAM_ANGLES[0], right_ray_angles[1] + LEFT_CAM_ANGLES[1]))
    p1 = numpy.array([LEFT_CAM_OFFSET[0], LEFT_CAM_OFFSET[1], LEFT_CAM_OFFSET[2]])
    p2 = numpy.array([-LEFT_CAM_OFFSET[0], LEFT_CAM_OFFSET[1], LEFT_CAM_OFFSET[2]])
    # minimize squared distance between r1 and r2
    # (d1 * d1) * t1 + (d1 * d2) * t2 = (p2 - p1) * d1
    # (d1 * d2) * t1 + (d2 * d2) * t2 = (p2 - p1) * d2
    #                v
    # A = d1 * d1  B = d1 * d2  C = (p2 - p1) * d1  D = d2 * d2  E = (p2 - p1) * d2
    a = d1[0] * d1[0] + d1[1] * d1[1] + d1[2] * d1[2]
    b = d1[0] * d2[0] + d1[1] * d2[1] + d1[2] * d2[2]
    # p1 and p2 symmetrical across yz plane, xz and xy identical -> 0
    c = (-2 * p1[0]) * d1[0] + 0 + 0
    d = d2[0] * d2[0] + d2[1] * d2[1] + d2[2] * d2[2]
    e = (-2 * p1[0]) * d2[0] + 0 + 0
    den = a * d - b**2
    t1 = (c * d - b * e) / den
    t2 = -(a * e - b * c) / den
    q1 = numpy.array(p1) + t1 * numpy.array(d1)
    q2 = numpy.array(p2) + t2 * numpy.array(d2)
    distance = dist(q1, q2)
    if distance > 0.1:
        pass#raise StandbyTransition(f'Cameras localize object to farther than 0.1m apart ({distance}m)')
    location = (q1 + q2) / 2
    store_location(monotonic(), location)
    return location


def store_location(timestamp: float, location: numpy.typing.NDArray[numpy.float64]) -> None:
    """Adds the location at its timestamp to the stored history. Stores most recent 15 entries.
    """
    if len(_history) == 15:
        _history.pop()
    _history.insert(0, (timestamp, location))
    return


def get_location_history() -> List[Tuple[float, Tuple[float, float, float]]]:
    """Returns the last 15 locations and when it was detected.
    :return: list of timestamp and (x,y,z) metre coordinate sets
    """
    return _history
