from time import monotonic

from handler import Handler
from ..filter import acc_threshold


class LogAccHandler(Handler):
    """Connection handler for logging values to terminal.
    """

    start_time = 0
    last_update = 0

    def __init__(self):
        self.max_acc = [0.0, 0.0, 0.0]
        """Maximum x,y,z acceleration received for active duration"""
        self.count = 0
        """Measurements received"""

    def step(self, acc: list[float]) -> None:
        # set start time if not set
        if self.start_time == 0:
            self.start_time = monotonic()
        # filter acceleration
        acc = acc_threshold(acc)
        # check each dimension for new highest acceleration
        for dim in range(0, 3):
            self.max_acc[dim] = max(self.max_acc[dim], acc[dim])
        # print time since start, and current and max of x,y,z acceleration
        print(
            f"{monotonic()-self.start_time:10.7}s "
            f"({self.count:7}): "
            f"{acc[0]:10.7f} ({self.max_acc[0]:10.7f}) "
            f"{acc[1]:10.7f} ({self.max_acc[1]:10.7f}) "
            f"{acc[2]:10.7f} ({self.max_acc[2]:10.7f})",
            end="\r"
        )
        self.update_timer()

    def update_timer(self) -> None:
        self.last_update = monotonic()
