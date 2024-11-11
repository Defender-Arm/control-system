def acc_threshold(acc: list[float], thresh: float = 0.1) -> list[float]:
    """
    Filters acceleration measurements to reduce noise around
    zero point.
    :param acc: x,y,z acceleration unfiltered
    :param thresh: if absolute value input greater than this value,
    will not be zeroed
    :return: x,y,z acceleration after filter
    """

    return [(a if abs(a) > thresh else 0.0) for a in acc]
