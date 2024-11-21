from numpy import array, cumsum, gradient


def integrate_list(time_delta: list[float], vals: list[float]) -> list[float]:
    """Convert timestamps and acceleration or velocity
    to velocity or position, respectively"""

    return list(cumsum(array(vals) * gradient(array(time_delta))))
