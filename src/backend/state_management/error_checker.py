from typing import List, Tuple


MAX_TIME = 0.2  # s
MAX_DIST = 1  # m


def verify_track(history: List[Tuple[float, Tuple[float, float, float]]]) -> bool:
    """Verifies inputs for error cases.
    :return: If track is valid
    """
    timestamps = [frame[0] for frame in history]
    locations = [frame[1] for frame in history]
    return _verify_time(timestamps) and _verify_location(locations)


def _verify_time(timestamps: List[float]) -> bool:
    """Ensures time frame between tracking updates is reasonable.
    :return: If timestamps are valid
    """
    for i in range(len(timestamps) - 1):
        if abs(timestamps[i] - timestamps[i+1]) > MAX_TIME:
            return False
    return True


def _verify_location(locations: List[Tuple[float, float, float]]) -> bool:
    """Ensures locations at each time frame are a realistic distance apart.
    :return: If locations are valid
    """
    for i in range(len(locations) - 1):
        if (
                (locations[i][0] - locations[i+1][0])**2 +
                (locations[i][1] - locations[i+1][1])**2 +
                (locations[i][2] - locations[i+1][2])**2
        ) ** 0.5 > MAX_DIST:
            return False
    return True
