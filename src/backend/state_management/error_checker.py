from typing import List, Tuple

from src.backend.error.standby_transition import StandbyTransition


MAX_TIME = 0.2  # s
MAX_DIST = 1  # m


def verify_track(history: List[Tuple[float, Tuple[float, float, float]]]) -> None:
    """Verifies inputs for error cases.
    :raise StandbyTransition: Locations are too far apart in time or space
    """
    timestamps = [frame[0] for frame in history]
    locations = [frame[1] for frame in history]
    _verify_time(timestamps)
    _verify_location(locations)


def _verify_time(timestamps: List[float]) -> None:
    """Ensures time frame between tracking updates is reasonable.
    :raise StandbyTransition: Locations are too far apart in time
    """
    for i in range(len(timestamps) - 1):
        diff = abs(timestamps[i] - timestamps[i+1])
        if diff > MAX_TIME:
            raise StandbyTransition(f'Past timesteps {i} and {i+1} are too far apart ({diff}s)')



def _verify_location(locations: List[Tuple[float, float, float]]) -> None:
    """Ensures locations at each time frame are a realistic distance apart.
    :raise StandbyTransition: Locations are too far apart in space
    """
    for i in range(len(locations) - 1):
        distance = (
               (locations[i][0] - locations[i+1][0])**2 +
               (locations[i][1] - locations[i+1][1])**2 +
               (locations[i][2] - locations[i+1][2])**2
        ) ** 0.5
        if distance > MAX_DIST:
            raise StandbyTransition(f'Locations at past timesteps {i} and {i+1} are too far apart ({distance}m)')

