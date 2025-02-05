from src.backend.external_management.connections import (
    LEFT_CAM_OFFSET,
    LEFT_CAM_ANGLES,
    CAM_FOV,
    CAM_RES
)
from src.backend.error.standby_transition import StandbyTransition

import cv2
import numpy
from typing import List, Optional, Tuple


LOWER_RED_1 = numpy.ndarray([0, 120, 70])
UPPER_RED_1 = numpy.ndarray([10, 255, 255])
LOWER_RED_2 = numpy.ndarray([170, 120, 70])
UPPER_RED_2 = numpy.ndarray([180, 255, 255])


_history = []


def find_in_image(image: numpy.ndarray) -> Optional[Tuple[Tuple[int, int], float]]:
    """Finds the pixel coordinates of the centre of the object in the image.
    :return: Pixel location, (x, y) from top left, angle from upwards,
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
        return None


def create_ray(pixel_x: int, pixel_y: int) -> Tuple[float, float]:
    """Calculates angles for line in real space which passes from the center of
    the camera through the object in the image.
    :return: Angles in radians from camera along x-axis (right), then y-axis (up)
    """
    angle_x = (pixel_x / CAM_RES[0]) * CAM_FOV - (CAM_FOV / 2)
    vertical_fov = (CAM_RES[1] / CAM_RES[0]) * CAM_FOV
    angle_y = (pixel_y / CAM_RES[1]) * vertical_fov - (vertical_fov / 2)
    return angle_x, angle_y


def locate_object(
        left_ray_angles: Tuple[float, float],
        right_ray_angles: Tuple[float, float]
) -> Tuple[float, float, float]:
    """Finds where two rays intersect or are the closest to intercepting.
    :raise RuntimeError: Rays do not intersect and shortest distance between them is greater than 0.1 metre
    :return: Metres from base joint; x-axis, then y-axis, then z-axis
    """
    raise StandbyTransition("Unimplemented")


def store_location(timestamp: float, location: Tuple[float, float, float]) -> None:
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
