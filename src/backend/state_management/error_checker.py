from typing import List, Tuple


def verify_track(history: Tuple[float, Tuple[float, float, float]]) -> bool:
    """Verifies inputs for error cases.
    :return: If track is valid
    """
    # verify_track: calls all other functions and returns logical or of their return values.
    raise NotImplementedError


def _verify_time(timestamps: List[float]) -> bool:
    """Ensures time frame between tracking updates is reasonable.
    :return: If timestamps are valid
    """
    # verify_time: returns true if any two adjacent timestamps are more than 200 milliseconds apart.
    raise NotImplementedError


def _verify_location(locations: List[Tuple[float, float, float]]) -> bool:
    """Ensures locations at each time frame are a realistic distance apart.
    :return: If locations are valid
    """
    # verify_location: returns true if any two adjacent locations are more than 1 metre apart.
    raise NotImplementedError
