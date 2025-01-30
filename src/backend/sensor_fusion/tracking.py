from src.backend.external_management.connections import (
    LEFT_CAM_OFFSET,
    LEFT_CAM_ANGLES,
    CAM_FOV,
    CAM_RES
)

from numpy import ndarray
from typing import List, Tuple


SWORD_FILTER = None


_history = []


def find_in_image(image: ndarray) -> Tuple[int, int]:
    """Finds the pixel coordinates of the centre of the object in the image.
    :return: Pixel location, (x, y) from top left
    """
    raise NotImplementedError


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
    raise RuntimeError


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
