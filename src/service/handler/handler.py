from abc import ABC, abstractmethod


class Handler(ABC):

    @property
    @abstractmethod
    def start_time(self):
        """Time of first measurement"""
        return

    @start_time.setter
    @abstractmethod
    def start_time(self, time: float):
        return

    @property
    @abstractmethod
    def last_update(self):
        """Time of last received measurement"""
        return

    @abstractmethod
    def step(self, acc: list[float]) -> None:
        """Handles one set of read sensor values."""
        return

    @abstractmethod
    def update_timer(self) -> None:
        """Updates handler last timestamp to current time."""
        return
