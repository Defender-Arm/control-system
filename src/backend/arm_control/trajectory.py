from typing import List, Tuple
import numpy


def calculate_trajectory(history: List[Tuple[float, numpy.typing.NDArray[numpy.float64]]]):
    """Using past locations of object, predict parabola of sword swing.
    :return: Trajectory of estimated swing arc
    """
    raise NotImplementedError


def calculate_collision() -> numpy.typing.NDArray[numpy.float64]:
    """Calculate interception point of line and arm workspace.
    :return: intercept as 3D point
    """
    raise NotImplementedError


def simple_trajectory(location: numpy.typing.NDArray[numpy.float64]) -> numpy.typing.NDArray[numpy.float64]:
    """Exaggerates position of object to force larger response from arm.
    :return: New exaggerated location
    """
    location[0] = location[0]
    location[1] = location[1]
    location[2] = location[2] - 0.25
    return location
