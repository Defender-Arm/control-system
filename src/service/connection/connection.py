from abc import ABC, abstractmethod


class Connection(ABC):

    @property
    @abstractmethod
    def run_time(self):
        """How long to read measurements before disconnecting
        automatically"""
        return

    @run_time.setter
    @abstractmethod
    def run_time(self, sec: int):
        return

    @abstractmethod
    def connect(self):
        """Connect to ESP32 board and read values until
        `run_time` is exceeded."""
        return
